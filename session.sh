#/bin/bash

TOKEN="${1}"
PROFILE="${2}"

if [[ -n "$TOKEN" ]] && [[ ${#TOKEN} == 6 ]]; then

  if [[ -n "$PROFILE" ]]; then
    PROFILE_FLAG="--profile ${PROFILE}"
  fi

  MFA_SERIAL=$(aws iam get-user $PROFILE_FLAG --query User.Arn --output text)

	# If we get an error calling iam get-user $MFA_SERIAL will always be empty
	if ! [[ -n "$MFA_SERIAL" ]]; then

		# Assuming the error reporting doesn't change greatly this should work nicely
		MFA_SERIAL=$(aws iam get-user $PROFILE_FLAG --output json 2>&1> /dev/null | sed -n 's/.*\(arn.*\).*/\1/p')

		if ! [[ -n "$MFA_SERIAL" ]]; then

			echo "Failed to obtain MFA serial arn. Make sure to check profile parameter is correct"
			return 1

		fi

	fi


  MFA_SERIAL=${MFA_SERIAL/user/mfa}

  if [[ -n "$PROFILE" ]]; then
    echo "Using profile so removing env credentials"
    temp_st=$AWS_SESSION_TOKEN
    temp_sak=$AWS_SECRET_ACCESS_KEY
    temp_aki=$AWS_ACCESS_KEY_ID
    unset AWS_SESSION_TOKEN 2> /dev/null
    unset AWS_SECRET_ACCESS_KEY 2> /dev/null
    unset AWS_ACCESS_KEY_ID 2> /dev/null
  fi
  
  aws sts get-session-token \
    --output json \
    $PROFILE_FLAG $PROFILE \
    --duration-seconds 900 \
    --serial-number $MFA_SERIAL \
    --token-code $TOKEN > ./SESSION

  if [ "$?" -ne "0" ]; then

    echo "Failed to get session token. Make sure token is first parameter and MFA device is in sync."

    if [[ -n "$PROFILE" ]]; then
      echo "Restoring env credentials"
      export AWS_SESSION_TOKEN=$temp_st
      export AWS_SECRET_ACCESS_KEY=$temp_sak
      export AWS_ACCESS_KEY_ID=$temp_aki
    fi
    rm ./SESSION 
    return 1
  fi

  export AWS_SECRET_ACCESS_KEY=$(grep '"SecretAccessKey"' ./SESSION  | cut -d '"' -f4)
  export AWS_SESSION_TOKEN=$(grep '"SessionToken"' ./SESSION  | cut -d '"' -f4)
  export AWS_ACCESS_KEY_ID=$(grep '"AccessKeyId"' ./SESSION  | cut -d '"' -f4)
  printf " ---\nSession successfully set for profile/user: "$PROFILE"\n ---\n"
  rm ./SESSION

else

    echo "Please pass a MFA token as parameters and a configured aws cli profile name, in that order"

fi

