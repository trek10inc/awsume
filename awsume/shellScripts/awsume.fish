#!/bin/fish
#AWSume - a bash script shell wrapper to awsumepy, a cli that makes using AWS IAM credentials easy

#AWSUME_FLAG - what awsumepy told the shell to 
#AWSUME_n - the data from awsumepy
set -x AWSUME_OUTPUT (awsumepy $argv | tr ' ' '\n')

set -x AWSUME_FLAG $AWSUME_OUTPUT[1]
set -x AWSUME_1 $AWSUME_OUTPUT[2]
set -x AWSUME_2 $AWSUME_OUTPUT[3]
set -x AWSUME_3 $AWSUME_OUTPUT[4]
set -x AWSUME_4 $AWSUME_OUTPUT[5]
set -x AWSUME_5 $AWSUME_OUTPUT[6]
set -x AWSUME_6 $AWSUME_OUTPUT[7]


#if incorrect flag/help
if [ "$AWSUME_FLAG" = "usage:" ]
    awsumepy -h
#if version check
else if [ "$AWSUME_FLAG" = "Version" ]
    awsumepy -v
#if -l flag passed
else if [ "$AWSUME_FLAG" = "Listing..." ]
    awsumepy -l
#set up auto-refreshing role
else if [ "$AWSUME_FLAG" = "Auto" ]
    set --erase AWS_SECRET_ACCESS_KEY
    set --erase AWS_SESSION_TOKEN
    set --erase AWS_SECURITY_TOKEN
    set --erase AWS_ACCESS_KEY_ID
    set --erase AWS_REGION
    set --erase AWS_DEFAULT_REGION
    set --erase AWS_PROFILE
    set --erase AWS_DEFAULT_PROFILE
    set --erase AWSUME_PROFILE

    #set the PROFILE that will contain the session credentials
    export AWS_PROFILE=$AWSUME_1
    export AWS_DEFAULT_PROFILE=$AWSUME_1

    if [ ! "$AWSUME_2" = "None" ]
        export AWS_REGION=$AWSUME_2
        export AWS_DEFAULT_REGION=$AWSUME_2
    end

    export AWSUME_PROFILE=$AWSUME_3
    #run the background autoawsume process
    autoawsume & disown

#user sent the set --erase variables flag
else if [ "$AWSUME_FLAG" = "unset" ]
    set --erase AWS_PROFILE
    set --erase AWS_DEFAULT_PROFILE
    set --erase AWS_SECRET_ACCESS_KEY
    set --erase AWS_SESSION_TOKEN
    set --erase AWS_SECURITY_TOKEN
    set --erase AWS_ACCESS_KEY_ID
    set --erase AWS_REGION
    set --erase AWS_DEFAULT_REGION
    set --erase AWSUME_PROFILE

    #show the commands to set --erase these environment variables
    for AWSUME_var in $argv
        #show commands
        if [ "$AWSUME_var" = "-s" ]
            echo set --erase AWS_PROFILE
            echo set --erase AWS_DEFAULT_PROFILE
            echo set --erase AWS_SECRET_ACCESS_KEY
            echo set --erase AWS_SESSION_TOKEN
            echo set --erase AWS_SECURITY_TOKEN
            echo set --erase AWS_ACCESS_KEY_ID
            echo set --erase AWS_REGION
            echo set --erase AWS_DEFAULT_REGION
            echo set --erase AWSUME_PROFILE
        end
    end
    exit

#user sent the kill flag, so  no more
else if [ "$AWSUME_FLAG" = "Kill" ]
    set --erase AWS_PROFILE
    set --erase AWS_DEFAULT_PROFILE
    set --erase AWS_SECRET_ACCESS_KEY
    set --erase AWS_SESSION_TOKEN
    set --erase AWS_SECURITY_TOKEN
    set --erase AWS_ACCESS_KEY_ID
    set --erase AWS_REGION
    set --erase AWS_DEFAULT_REGION
    set --erase AWSUME_PROFILE
    exit

else if [ "$AWSUME_FLAG" = "Stop" ]
    if [ "auto-refresh-$AWSUME_1" = "$AWS_PROFILE" ]
        set --erase AWS_PROFILE
        set --erase AWS_DEFAULT_PROFILE
    end
    exit

#awsume the PROFILE
else if [ "$AWSUME_FLAG" = "Awsume" ]
    set --erase AWS_SECRET_ACCESS_KEY
    set --erase AWS_SESSION_TOKEN
    set --erase AWS_SECURITY_TOKEN
    set --erase AWS_ACCESS_KEY_ID
    set --erase AWS_REGION
    set --erase AWS_DEFAULT_REGION
    set --erase AWS_PROFILE
    set --erase AWS_DEFAULT_PROFILE
    set --erase AWSUME_PROFILE

    export AWS_ACCESS_KEY_ID=$AWSUME_1
    export AWS_SECRET_ACCESS_KEY=$AWSUME_2

    if [ ! "$AWSUME_3" = "None" ]
        export AWS_SESSION_TOKEN=$AWSUME_3
        export AWS_SECURITY_TOKEN=$AWSUME_3
    end

    if [ ! "$AWSUME_4" = "None" ]
        export AWS_REGION=$AWSUME_4
        export AWS_DEFAULT_REGION=$AWSUME_4
    end

    export AWSUME_PROFILE=$AWSUME_5

    #if enabled, show the exact commands to use in order to assume the role we just assumed
    for AWSUME_var in $argv
    
        #show commands
        if [ "$AWSUME_var" = "-s" ]
            echo export AWS_ACCESS_KEY_ID=$AWSUME_1
            echo export AWS_SECRET_ACCESS_KEY=$AWSUME_2

            if [ ! "$AWSUME_3" = "None" ]
                echo export AWS_SESSION_TOKEN=$AWSUME_3
                echo export AWS_SECURITY_TOKEN=$AWSUME_3
            end

            if [ ! "$AWSUME_4" = "None" ]
                echo export AWS_REGION=$AWSUME_4
                echo export AWS_DEFAULT_REGION=$AWSUME_4
            end

            echo export AWSUME_PROFILE=$AWSUME_5

        end
    end
end
