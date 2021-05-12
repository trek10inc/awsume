#!/bin/fish

#AWSUME_FLAG - what awsumepy told the shell to do
#AWSUME_n - the data from awsumepy
set AWSUME_OUTPUT (awsumepy $argv)
set AWSUME_STATUS $status
echo $AWSUME_OUTPUT | read AWSUME_FLAG AWSUME_1 AWSUME_2 AWSUME_3 AWSUME_4 AWSUME_5 AWSUME_6 AWSUME_7

# remove carraige return
set -gx AWSUME_FLAG (echo $AWSUME_FLAG | tr -d '\r')

if test "$AWSUME_FLAG" = "usage:"
  awsumepy $argv


else if test "$AWSUME_FLAG" = "Version"
  awsumepy $argv


else if test "$AWSUME_FLAG" = "Listing..."
  awsumepy $argv


else if test "$AWSUME_FLAG" = "Auto"
  set -e AWS_ACCESS_KEY_ID
  set -e AWS_SECRET_ACCESS_KEY
  set -e AWS_SESSION_TOKEN
  set -e AWS_REGION
  set -e AWS_DEFAULT_REGION
  set -e AWS_PROFILE
  set -e AWS_DEFAULT_PROFILE
  set -e AWSUME_EXPIRATION
  set -e AWSUME_PROFILE
  set -e AWSUME_COMMAND

  set -gx AWSUME_COMMAND $argv
  set -gx AWS_PROFILE $AWSUME_1
  set -gx AWS_DEFAULT_PROFILE $AWSUME_1

  if test "$AWSUME_2" != "None"
    set -gx AWS_REGION $AWSUME_2
    set -gx AWS_DEFAULT_REGION $AWSUME_2
  end
  if test "$AWSUME_3" != "None"
    set -gx AWSUME_PROFILE $AWSUME_3
  end

  #run the background autoawsume process
  autoawsume & disown


else if test "$AWSUME_FLAG" = "Unset"
  set -e AWS_ACCESS_KEY_ID
  set -e AWS_SECRET_ACCESS_KEY
  set -e AWS_SESSION_TOKEN
  set -e AWS_REGION
  set -e AWS_DEFAULT_REGION
  set -e AWS_PROFILE
  set -e AWS_DEFAULT_PROFILE
  set -e AWSUME_EXPIRATION
  set -e AWSUME_PROFILE
  set -e AWSUME_COMMAND

  if contains -- -s $argv
    echo set -e AWS_ACCESS_KEY_ID
    echo set -e AWS_SECRET_ACCESS_KEY
    echo set -e AWS_SESSION_TOKEN
    echo set -e AWS_REGION
    echo set -e AWS_DEFAULT_REGION
    echo set -e AWS_PROFILE
    echo set -e AWS_DEFAULT_PROFILE
    echo set -e AWSUME_EXPIRATION
    echo set -e AWSUME_PROFILE
    echo set -e AWSUME_COMMAND
  end
  exit 0

else if test "$AWSUME_FLAG" = "Kill"
  set -e AWS_ACCESS_KEY_ID
  set -e AWS_SECRET_ACCESS_KEY
  set -e AWS_SESSION_TOKEN
  set -e AWS_REGION
  set -e AWS_DEFAULT_REGION
  set -e AWS_PROFILE
  set -e AWS_DEFAULT_PROFILE
  set -e AWSUME_EXPIRATION
  set -e AWSUME_PROFILE
  set -e AWSUME_COMMAND
  exit 0


else if test "$AWSUME_FLAG" = "Stop"
  if test "auto-refresh-$AWSUME_1" = "$AWS_PROFILE"
      set -e AWS_ACCESS_KEY_ID
      set -e AWS_SECRET_ACCESS_KEY
      set -e AWS_SESSION_TOKEN
      set -e AWS_REGION
      set -e AWS_DEFAULT_REGION
      set -e AWS_PROFILE
      set -e AWS_DEFAULT_PROFILE
      set -e AWSUME_EXPIRATION
      set -e AWSUME_PROFILE
      set -e AWSUME_COMMAND
  end
  exit 0


else if test "$AWSUME_FLAG" = "Awsume"
  set -e AWS_ACCESS_KEY_ID
  set -e AWS_SECRET_ACCESS_KEY
  set -e AWS_SESSION_TOKEN
  set -e AWS_REGION
  set -e AWS_DEFAULT_REGION
  set -e AWS_PROFILE
  set -e AWS_DEFAULT_PROFILE
  set -e AWSUME_EXPIRATION
  set -e AWSUME_PROFILE
  set -e AWSUME_COMMAND

  set -gx AWSUME_COMMAND $argv
  if test "$AWSUME_1" != "None"
    set -gx AWS_ACCESS_KEY_ID $AWSUME_1
  end
  if test "$AWSUME_2" != "None"
    set -gx AWS_SECRET_ACCESS_KEY $AWSUME_2
  end
  if test "$AWSUME_3" != "None"
    set -gx AWS_SESSION_TOKEN $AWSUME_3
  end
  if test "$AWSUME_4" != "None"
    set -gx AWS_REGION $AWSUME_4
    set -gx AWS_DEFAULT_REGION $AWSUME_4
  end
  if test "$AWSUME_5" != "None"
    set -gx AWSUME_PROFILE $AWSUME_5
  end
  if test "$AWSUME_6" != "None"
    set -gx AWS_PROFILE $AWSUME_6
    set -gx AWS_DEFAULT_PROFILE $AWSUME_6
  end
  if test "$AWSUME_7" != "None"
    set -gx AWSUME_EXPIRATION $AWSUME_7
  end

  if contains -- -s $argv
    if test "$AWSUME_1" != "None"
      echo set -gx AWS_ACCESS_KEY_ID $AWSUME_1
    end
    if test "$AWSUME_2" != "None"
      echo set -gx AWS_SECRET_ACCESS_KEY $AWSUME_2
    end
    if test "$AWSUME_3" != "None"
      echo set -gx AWS_SESSION_TOKEN $AWSUME_3
    end
    if test "$AWSUME_4" != "None"
      echo set -gx AWS_REGION $AWSUME_4
      echo set -gx AWS_DEFAULT_REGION $AWSUME_4
    end
    if test "$AWSUME_5" != "None"
      echo set -gx AWSUME_PROFILE $AWSUME_5
    end
    if test "$AWSUME_6" != "None"
      echo set -gx AWS_PROFILE $AWSUME_6
      echo set -gx AWS_DEFAULT_PROFILE $AWSUME_6
    end
    if test "$AWSUME_7" != "None"
      echo set -gx AWSUME_EXPIRATION $AWSUME_7
    end
  end
end

exit $AWSUME_STATUS