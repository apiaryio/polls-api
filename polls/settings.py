import os


def get_env(key, default=True):
    value = os.environ.get(key, default)
    return (value == True or value.lower() == 'true' or value == '1' or
            value.lower() == 'yes')


# Enables the ability to create a question
CAN_CREATE_QUESTION = get_env('POLLS_CAN_CREATE_QUESTION')

# Enables the ability to delete a question
CAN_DELETE_QUESTION = get_env('POLLS_CAN_DELETE_QUESTION')

# Enables the ability to vote on a question
CAN_VOTE_QUESTION = get_env('POLLS_CAN_VOTE_QUESTION')

