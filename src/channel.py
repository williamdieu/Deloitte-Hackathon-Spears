'''
Author: Nikola Medimurac
Implementation of channel related backend functions
'''

import website_data as wd
from error import InputError, AccessError

# ******** Helper Functions for channel ***************
def get_user_id_and_channel_data(token, channel_id):
    '''
    This is a helper function that gets the user_id and channel data from website data
    given a token and channel id
    Raises input errors if invalid token is given, channel id doesnt exist or
    user is not a member of the channel
    '''
    # Get the id of the user calling the function from their token
    user_id = wd.get_id_from_token(token)
    if user_id is None:
        raise AccessError(description="Invalid token given")
    # Get the data of the specified channel, raise InputError if it doesnt exist
    channel_data = wd.get_data_with_id('channel data', channel_id)
    if channel_data is None:
        raise InputError(description="Invalid channel id given")
    # Check if the user is in the list of members in the channel
    if user_id not in channel_data['members']:
        raise AccessError(description="User is not a member of the channel")
    return user_id, channel_data

def message_data_to_message(user_id, message_data):
    '''
    This function takes in an entry from the list of "message data"
    and converts it to a dictionary of type message (described in specs)
    '''
    message = {}
    message['message_id'] = message_data['id']
    message['u_id'] = message_data['sender id']
    message['message'] = message_data['contents']
    message['time_created'] = message_data['timestamp']
    # Get the react data for the message
    message['reacts'] = []
    for react_id in wd.get_valid_react_ids():
        # Create react data for each react id, set react id first
        react_data = {}
        react_data['react_id'] = react_id
        # Iterate through the list of reacts and add them to the list if same id
        react_data['u_ids'] = []
        for react in message_data['reacts']:
            if react['react id'] == react_id:
                react_data['u_ids'].append(react['user id'])
        # Check if user id is in the list
        if user_id in react_data['u_ids']:
            react_data['is_this_user_reacted'] = True
        else:
            react_data['is_this_user_reacted'] = False
        # Attach react data to list of reacts
        message['reacts'].append(react_data)
    message['is_pinned'] = message_data['pinned']
    return message


def user_data_to_member(user_data, port):
    '''
    This function takes in an entry from the list of "user data"
    and converts it to a dictionary of type member (described in specs)
    '''
    member = {}
    member['u_id'] = user_data['id']
    member['name_first'] = user_data['first name']
    member['name_last'] = user_data['last name']
    member['profile_img_url'] = user_data['img name']
    # If they have a profile picture then add that field in
    if user_data['img name'] != '':
        member['profile_img_url'] = 'http://localhost:' + str(port) + '/profile_imgs/'
        member['profile_img_url'] += user_data['img name'] + '.jpg'
    return member

# ***************** Website Functions *****************
def channel_invite(token, channel_id, add_user_id):
    '''
    Function for inviting another user to a channel
    Automatically adds the other user to the channel if valid
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err
    # Check that the user being added is not already in the channel
    if add_user_id in channel_data['members']:
        raise InputError(description="User is already in channel")
    # Check the user being added is a valid user id
    all_user_data = wd.get_data("user data")
    if not any(user_data['id'] == add_user_id for user_data in all_user_data):
        raise InputError(description="User id being added does not exist")
    # Add the new user to the list of members in the channel and owners if slackr owner
    channel_data['members'].append(add_user_id)
    add_user_data = wd.get_data_with_id('user data', add_user_id)
    if add_user_data['permission id'] == 1:
        channel_data['owners'].append(user_id)
    wd.set_data_with_id("channel data", channel_id, channel_data)
    return {}

def channel_details(token, channel_id, port):
    '''
    Function for inviting another user to a channel
    Automatically adds the other user to the channel if valid
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err
    # Create dictionary containing channel details
    channel_dict = {"name" : channel_data["name"], "owner_members" : [], "all_members" : []}
    # Add owner members data to the list inside channel_dict
    for user_id in channel_data['owners']:
        if user_id is not None:
            user_data = wd.get_data_with_id('user data', user_id)
            channel_dict['owner_members'].append(user_data_to_member(user_data, port))
    # Add all members data to the list inside channel_dict
    for user_id in channel_data['members']:
        if user_id is not None:
            user_data = wd.get_data_with_id('user data', user_id)
            channel_dict['all_members'].append(user_data_to_member(user_data, port))
    return channel_dict

def channel_messages(token, channel_id, start):
    '''
    Function to get the messages posted in a channel
    Returns a list of up to 50 messages from the starting index it is given
    It also returns the starting index, the ending index and the ending index is
    -1 if at the end of the list of messages
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err

    # Get the list of message ids in the channel
    message_id_list = channel_data['messages']
    # Reverse the list so the most recent message is at the beggining
    message_id_list = message_id_list[::-1]
    # Check that the start index given is not greater then the number of message
    if start > len(message_id_list):
        raise InputError(description="Start greater than number of messages")
    # Check if the start index is pointing to the last thing in the list
    if start == len(message_id_list):
        return {'messages' : [], 'start' : start, 'end' : -1}
    # Iterate through up to 50 times and create a list of messsages
    messages_list = []
    for i in range(50):
        index = start + i
        # Add message with id to the list
        message_data = wd.get_data_with_id('message data', message_id_list[index])
        # Convert the message data to match the specs before appending
        message = message_data_to_message(user_id, message_data)
        messages_list.append(message)
        # Check if at the end of the message list if so set end as -1 and break
        if index == len(message_id_list) - 1:
            end = -1
            break
        # Set end to the index of the next number in message list
        end = index + 1
    return {'messages' : messages_list, 'start' : start, 'end' : end}

def channel_leave(token, channel_id):
    '''
    Function to user to remove themself from a given channel
    This removes their id from the member list in channel data
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err
    # Remove user from list of members
    channel_data['members'].remove(user_id)
    # Also remove user from owners if they are an owner
    if user_id in channel_data['owners']:
        channel_data['owners'].remove(user_id)
    # Update channel data in website_data
    wd.set_data_with_id("channel data", channel_id, channel_data)
    return {}

def channel_join(token, channel_id):
    '''
    Function that add the user automatically to the channel if valid
    This add their user id value to the member list of the channel data
    '''
    # Since joining is the only function that requires not being in the channel,
    # a helper function wont be used to simplify the initial setup
    # Get user id and channel data from token and channel_id
    user_id = wd.get_id_from_token(token)
    if user_id is None:
        raise AccessError(description="Invalid token given")
    # Get the data of the specified channel, raise InputError if it doesnt exist
    channel_data = wd.get_data_with_id('channel data', channel_id)
    if channel_data is None:
        raise InputError(description="Invalid channel id given")
    # Check that the user being added is not already in the channel
    if user_id in channel_data['members']:
        raise InputError(description="User is already in channel")
    # Check if the channel is private and the user is not the slackr owner
    if not channel_data['public'] and user_id != 0:
        raise AccessError(description="Cannot join as channel is private")
    # Add user id to list of channel members and add to owners if slackr owner
    channel_data['members'].append(user_id)
    user_data = wd.get_data_with_id('user data', user_id)
    if user_data['permission id'] == 1:
        channel_data['owners'].append(user_id)
    wd.set_data_with_id("channel data", channel_id, channel_data)
    return {}


def channel_addowner(token, channel_id, add_user_id):
    '''
    Function for a user to make another user an owner of a channel
    If the user being added is not in the channel already they are added to it
    User calling this must be owner in the channel
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err
    # Check that user is in owners list and if not return AccessError
    if user_id not in channel_data['owners']:
        raise AccessError(description="User is not an owner of the channel")
    # Check the user being added is a valid user id
    all_user_data = wd.get_data("user data")
    if not any(user_data['id'] == add_user_id for user_data in all_user_data):
        raise InputError(description="User id being added does not exist")
    # Check that the user being added is not already an owner of the channel
    if add_user_id in channel_data['owners']:
        raise InputError(description="User being added is already an owner of the channel")
    # Add user id to list of channel owners and add to members if not already
    channel_data['owners'].append(add_user_id)
    if add_user_id not in channel_data['members']:
        channel_data['members'].append(add_user_id)
    wd.set_data_with_id("channel data", channel_id, channel_data)
    return {}

def channel_removeowner(token, channel_id, rem_user_id):
    '''
    Function for a user to remove another user as an owner of a channel
    User calling this must be owner in the channel
    '''
    # Get user id and channel data from token and channel_id
    try:
        user_id, channel_data = get_user_id_and_channel_data(token, channel_id)
    except Exception as err:
        raise err
    # Check that user is in owners list and if not return AccessError
    if user_id not in channel_data['owners']:
        raise AccessError(description="User is not an owner of the channel")
    # Check that the user being removed is an owner of the channel
    if rem_user_id not in channel_data['owners']:
        raise InputError(description="User being removed is not an owner of the channel")
    # Check that it is not the slackr owner being removed as this breaks assumptions
    rem_user_data = wd.get_data_with_id('user data', rem_user_id)
    if rem_user_data['permission id'] == 1:
        raise AccessError(description="Cannot remove Slackr owner as channel owner")
    # Now remove the users id from the list of owners
    channel_data['owners'].remove(rem_user_id)
    wd.set_data_with_id("channel data", channel_id, channel_data)
    return {}