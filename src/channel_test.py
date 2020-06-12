# ************************************************
# File for testing functions related to channel
# Author: Nikola Medimurac
# Date Started: 3/3/2020
# ************************************************
# Functions tested in this file include:
# channel.channel_invite()
# channel.channel_details()
# channel.channel_messages()
# channel.channel_leave()
# channel.channel_join()
# channel.channel_addowner()
# channel.channel_removeowner()

'''
Tests for the implementation of channel
'''

# pylint: disable=redefined-outer-name,global-statement,invalid-name

from datetime import datetime
import pytest
import auth
import channel
import message
import channels
import website_data as wd


@pytest.fixture
def make_two_users():
    '''
    create fixture that resets the server state so that there are only 2 users
    '''
    wd.clear_all_data()
    user1 = auth.auth_register('user1@gmail.com', 'thisismypassword', 'myfirstname', 'mylastname')
    user2 = auth.auth_register('myemail@gmail.com', '123idk', 'name', 'anothername')
    return (user1, user2)


def test_channel_invite_normal(make_two_users):
    '''
    Test invites with normal valid inputs
    Perform this by making a user invite another to a public and private channel
    '''
    # Get data for two users
    user1, user2 = make_two_users
    # Create a public and private channel with user 1 in it
    channel_1_name = 'public ch'
    channel_2_name = 'private ch'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channel_2_id = channels.channels_create(user1['token'], channel_2_name, False)['channel_id']

    # Get user 1 to invite user 2 to channels, they should automatically be added to it
    channel.channel_invite(user1['token'], channel_1_id, user2['u_id'])
    channel.channel_invite(user1['token'], channel_2_id, user2['u_id'])

    # Check user 2 is in the the channels now by checking channels.channels_list
    # and assuming it works
    assert (channels.channels_list(user2['token'])['channels']) == (
        [{'channel_id': channel_1_id,
          'name': channel_1_name},
         {'channel_id': channel_2_id,
          'name': channel_2_name}]
    )


def test_channel_join_normal(make_two_users):
    '''
    Test joining function with normal valid inputs
    This involves creating a public and private channel by user 1 and user 2
    Since user 1 will be admin it should be able to join both of user 2 channels
    '''
    # Get data for two users
    user1, user2 = make_two_users
    # Create a public and private channel with user 1 in it
    channel_1_name = 'public user1'
    channel_2_name = 'public user2'
    channel_3_name = 'private user1'
    channel_4_name = 'private user2'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channel_2_id = channels.channels_create(user2['token'], channel_2_name, True)['channel_id']
    channel_3_id = channels.channels_create(user1['token'], channel_3_name, False)['channel_id']
    channel_4_id = channels.channels_create(user2['token'], channel_4_name, False)['channel_id']

    # Get user 1 to join both user 2s channels, and user 2 join user 1s public channel
    channel.channel_join(user1['token'], channel_2_id)
    channel.channel_join(user1['token'], channel_4_id)
    channel.channel_join(user2['token'], channel_1_id)

    # Check users are in correct channels now by checking channels.channels_list
    # and assuming it works
    assert (channels.channels_list(user1['token'])['channels']) == [
        {'channel_id': channel_1_id, 'name': channel_1_name},
        {'channel_id': channel_2_id, 'name': channel_2_name},
        {'channel_id': channel_3_id, 'name': channel_3_name},
        {'channel_id': channel_4_id, 'name': channel_4_name}
    ]
    assert (channels.channels_list(user2['token'])['channels']) == [
        {'channel_id': channel_1_id, 'name': channel_1_name},
        {'channel_id': channel_2_id, 'name': channel_2_name},
        {'channel_id': channel_4_id, 'name': channel_4_name}
    ]


def test_channel_leave_normal(make_two_users):
    '''
    Test leaving dunction with normal valid inputs
    Get user 1 to make 2 channels and join 2
    Then leave 1 channel made and 1 channel joined to check it works correctly
    in both situations
    Get user 2 to leave all their channels and check it works
    '''
    # Get data for two users
    user1, user2 = make_two_users
    # Create a public and private channel with user 1 in it
    channel_1_name = 'public user1'
    channel_2_name = 'public user2'
    channel_3_name = 'private user1'
    channel_4_name = 'private user2'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channel_2_id = channels.channels_create(user2['token'], channel_2_name, True)['channel_id']
    channel_3_id = channels.channels_create(user1['token'], channel_3_name, False)['channel_id']
    channel_4_id = channels.channels_create(user2['token'], channel_4_name, False)['channel_id']

    # Get user 1 to join both user 2s channels, and user 2 join user 1s public channel
    channel.channel_join(user1['token'], channel_2_id)
    channel.channel_join(user1['token'], channel_4_id)

    # Get users to leave channels
    channel.channel_leave(user1['token'], channel_1_id)
    channel.channel_leave(user1['token'], channel_4_id)
    channel.channel_leave(user2['token'], channel_2_id)
    channel.channel_leave(user2['token'], channel_4_id)

    # Check users are in correct channels now by checking channels.channels_list
    # and assuming it works
    assert (channels.channels_list(user1['token'])['channels']) == [
        {'channel_id': channel_2_id, 'name': channel_2_name},
        {'channel_id': channel_3_id, 'name': channel_3_name}
    ]
    assert (channels.channels_list(user2['token'])['channels']) == []


def test_channel_message_normal(make_two_users):
    '''
    Test messages command in channel with normal input
    '''
    # Get data for two users
    global message
    user1, user2 = make_two_users
    # Create a two channels where both users are in 1 and other only has 1
    # The second channel is used to make sure other channels are not affected by
    # messages not for them
    channel_1_name = 'test chan 1'
    channel_2_name = 'test chan 2'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channels.channels_create(user1['token'], channel_2_name, True)
    channel.channel_join(user2['token'], channel_1_id)

    # Add message to the chat the messages will be structured in the following way
    # user1 - 'a' 30 times, user2 - 'b' 21 times, user1 - 'c' 149 times
    # Also make a list to hold the timestamps for every message sent and a list of every messages is
    timestamps = []
    message_ids = []
    for i in range(200):
        if i < 30:
            message_ids.append(message.message_send(user1['token'], channel_1_id, 'a'))
        elif i < 51:
            message_ids.append(message.message_send(user2['token'], channel_1_id, 'b'))
        else:
            message_ids.append(message.message_send(user1['token'], channel_1_id, 'c'))
        # Get time stamp of when the message was sent
        timestamp = int(datetime.utcnow().timestamp()) + 36000
        # Convert to unix thing as specs say
        timestamps.append(timestamp)

    # Now read the message in the chat and check that we get the correct thing in return
    # Keep looping until the channel_message returns -1 indicating the end of message
    # Also need to remember we are going backwards through the messages
    end = 0
    message_number = 199
    while end != -1:
        channel_message = channel.channel_messages(user1['token'], channel_1_id, end)
        # Check start is correct and update end value to be the new end, start
        # should be previous end
        assert channel_message['start'] == end
        end = channel_message['end']
        for message in channel_message['messages']:
            # Check message is correct and from correct user
            if message_number < 30:
                assert message['message'] == 'a'
                assert message['u_id'] == user1['u_id']
            elif message_number < 51:
                assert message['message'] == 'b'
                assert message['u_id'] == user2['u_id']
            else:
                assert message['message'] == 'c'
                assert message['u_id'] == user1['u_id']
            # Check message id matches up
            assert message['message_id'] == message_ids[message_number]['message_id']
            # Check the time created mathes up, put an allowance of being off by
            # 1 second since the measurement is take after creating the message
            assert ((message['time_created'] == timestamps[message_number]) or (
                message['time_created'] == (timestamps[message_number] - 1)))
            # Decrement message number so we look at 1 number back in the list
            message_number -= 1
    # Above we checked the case where the message is a multiple of 50, now lets
    # check the case where it is not. Lets start at the 199th message so there
    # will only be 1 message for it to recieve
    channel_message = channel.channel_messages(user1['token'], channel_1_id, 199)
    assert channel_message['end'] == -1
    assert len(channel_message['messages']) == 1


def test_channel_details_normal(make_two_users):
    '''
    Test details command in channel with normal input
    '''
    # Get data for two users
    user1, user2 = make_two_users
    # make a third user for this test who does nothing to make sure they dont affect details
    auth.auth_register('user3@gmail.com', 'apassword', 'nameisfirst', 'nameislast')
    # get user 1 to create a channel and user 2 join it as a non owner
    channel_1_name = 'test chan 1'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channel.channel_join(user2['token'], channel_1_id)

    # Get the channel details and check if it is correct
    details = channel.channel_details(user1['token'], channel_1_id, 0)
    owners = details['owner_members']
    members = details['all_members']
    # Cheack name of channel is correct
    assert details['name'] == channel_1_name
    # Check owner members is correct
    assert len(owners) == 1
    assert owners == [
        {'u_id': user1['u_id'],
         'name_first': 'myfirstname',
         'name_last': 'mylastname',
         'profile_img_url' : ''}
    ]
    # Check all members is correct
    assert len(members) == 2
    assert members == [
        {'u_id': user1['u_id'],
         'name_first': 'myfirstname',
         'name_last': 'mylastname',
         'profile_img_url' : ''},
        {'u_id': user2['u_id'],
         'name_first': 'name',
         'name_last': 'anothername',
         'profile_img_url' : ''}
    ]


def is_owner(user_token, user_id, channel_id):
    '''
    Helper function for checking if user is an owner of a channel
    '''
    details = channel.channel_details(user_token, channel_id, 0)
    owners = details['owner_members']
    return any(owner['u_id'] == user_id for owner in owners)


def test_channel_owners_normal(make_two_users):
    '''
    Test that they are set correctly initially and that channel.channel_addowner()
    and channel.channel_removeowner() work
    '''
    # Get data for two users
    user1, user2 = make_two_users
    # Create a public and private channel with user 1 in it
    channel_1_name = 'public user1'
    channel_2_name = 'public user2'
    channel_1_id = channels.channels_create(user1['token'], channel_1_name, True)['channel_id']
    channel_2_id = channels.channels_create(user2['token'], channel_2_name, True)['channel_id']

    # Get the two users to join each others channels
    channel.channel_join(user1['token'], channel_2_id)
    channel.channel_join(user2['token'], channel_1_id)

    # Need to check channel.channel_details to work out if the user is an admin
    # Use helper function i made above to do this easier
    assert is_owner(user1['token'], user1['u_id'], channel_1_id)
    assert is_owner(user1['token'], user1['u_id'], channel_2_id)
    assert is_owner(user2['token'], user2['u_id'], channel_2_id)
    assert not is_owner(user2['token'], user2['u_id'], channel_1_id)

    # Give user 2 owner in channel 1 and remove user 2 as owner in channel 2
    channel.channel_addowner(user1['token'], channel_1_id, user2['u_id'])
    assert is_owner(user1['token'], user2['u_id'], channel_1_id)
    channel.channel_removeowner(user1['token'], channel_1_id, user2['u_id'])

    # Check if user 2 has the correct owner permissions now
    assert not is_owner(user2['token'], user2['u_id'], channel_1_id)
    assert is_owner(user2['token'], user2['u_id'], channel_2_id)

    # Make user 2 leave user 1's channel and add him as admin
    channel.channel_leave(user2['token'], channel_1_id)
    channel.channel_addowner(user1['token'], channel_1_id, user2['u_id'])
    assert is_owner(user1['token'], user2['u_id'], channel_1_id)