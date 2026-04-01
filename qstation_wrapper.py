# pylint: disable=C0103
# pylint: disable=w0603
# pylint: disable=R0913

#!/usr/bin/env python3
""" Provides a simplified API to the QStation Belleds controller, implementing
the API described at https://github.com/BelledsQ/QStation_API """

import json
import socket

# The socket used to communicate to the QStation
sock = None
# IP Address of the QStation
qstation_address = None

######### General #########

def connect(address):
    """ Saves connection info to be used when sending commands to the
    QStation Belleds device at a given IP Address """

    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    global qstation_address
    qstation_address = address

def get_lights():
    """ Gets a list of lights registered with the QStation """
    # NOTE: This function seems to be unfinished in the QStation firmware: it returns a list of
    # lights registered on the QStation, and also returns each bulb's settings... but fills inc
    # the settings with default values. the rgb colors are always returned as (10, 10, 10),
    # for instance
    # NOTE: The value of 'group' returned seems to be nonsensical
    cmd = {"cmd":"light_list"}
    resp = __send_resp_cmd(cmd)
    return resp

def ping():
    """ Pings the currently connected QStation """

    # Returns a utf-8 string b/c of the False command, used b/c
    # the QStation API description says this (and only this) command
    # does not return JSON
    resp = __send_resp_cmd({"cmd": "ping"}, False)
    return resp.split(",")
    
######### Groups #########

def group_list():
    """ Gets a list of lights, their setting info, and their group membership. """
    # NOTE: This seems to yield the same data as get_lights, but with the two additional parameters
    # of group_title and group_id
    cmd = {"cmd":"group_list"}
    return __send_resp_cmd(cmd)

def group_leds_list(group_id):
    """ Gets a list of all lights registered with the QStation, and their group membership status.
    status == 0 if not in a group, 1 if in the group with the given group_id, and 2 if they are in a
    different group """
    cmd = {
        "cmd":"group_leds_list",
        "group_id":group_id
    }
    return __send_resp_cmd(cmd)

def set_music_group(group_id):
    """ Toggles the music mode on a group with the given group id """
    cmd = {
        "cmd":"set_music_group",
        "music_group":group_id
    }

    __send_noresp_cmd(cmd)

def add_group(group_name):
    """ Adds a group to the QStation with the given group name """
    cmd = {
        "cmd": "add_group",
        "group_title":group_name
    }

    # TODO: This seems to (always?) return the incorrect group id. Investigate
    return __send_resp_cmd(cmd)

def delete_group(group_id):
    """ Deletes the group with the given group id """
    cmd = {
        "cmd": "del_group",
        "group_id":group_id
    }
    return __send_resp_cmd(cmd, False)

def set_group(sn, group_id):
    """ Adds the light with a given serial number to the group with the given group id """
    cmd = {
        "cmd":"set_group",
        "sn":sn,
        "group_id":group_id
    }
    return __send_resp_cmd(cmd, False)

def leave_group(sn, group_id):
    """ Removes a the light with a given serial number from the group with the given group id """
    cmd = {
        "cmd":" leave_group ",
        "sn":sn,
        "group_id":group_id
    }
    __send_noresp_cmd(cmd)


def set_group_title(group_id, title):
    """ Sets the title for a group with the group id """
    cmd = {
        "cmd":" set_group_title ",
        "group_id":group_id,
        "group_title":title
    }
    return __send_resp_cmd(cmd)

######### Individual Lights #########

def delete_light(sn):
    """ Deletes a light from the QStation """
    # TODO: I can't seem to notice this having any affect on the list of lights returned by
    # get_lights. Find out what this does
    cmd = {
        "cmd":" del_device",
        "sn":sn
    }

    __send_noresp_cmd(cmd)

def light_ctrl(color, mode, brightness, iswitch, matchValue, serials, group_id=-1):
    """ Set color, light mode, and brightness on the lights with the corresponding
    serial numbers given in serials. Receives a group_id (optional) to set lights in a group.
    The value of serials is irrelevant when using a group_id """

    # NOTE: Please see the parameter "sn_list" below: despite the QStation API examples
    # showing this being supplied multiple serial numbers, from my testing the QStation
    # will only change the settings on the first serial in the list. Seems to be a bug
    # (or at least mis-matched behavior)
    # NOTE: Also see the group_id param, optional. Leaving as -1 will make the 'group1' param
    # be omitted, below
    cmd = {
        "cmd": "light_ctrl",
        "r": color[0],
        "g": color[1],
        "b": color[2],
        "bright": brightness,
        "effect": mode, # 8 - white light, 9 - color
        "iswitch": iswitch,
        "matchValue": matchValue,
        "sn_list": [{"sn": sn} for sn in serials]
    }

    if group_id != -1:
        cmd['group1'] = group_id

    __send_noresp_cmd(cmd)

def set_light_title(title, sn):
    """ Sets the title of a light (it name) with the given serial number"""
    cmd = {
        "cmd":"set_title",
        "sn":sn,
        "title":title
    }

    # Note: It looks like set_title *does* send a response, despite what the API description
    # (https://github.com/BelledsQ/QStation_API/blob/master/Settings.md) says. We must use the
    # response-expecting version of send cmd here, otherwise the next response-expecting cmd will
    # receive the response for this cmd
    return __send_resp_cmd(cmd, False)

def set_music_led(sn):
    """ Toggles whether the LED with the given serial number does or does not sync with music """
    cmd = {"cmd": "set_musicled", "sn": sn}
    __send_noresp_cmd(cmd)

######### Misc #########

def save_lights(color, mode, angle, brightness, isSwitch, matchValue, serials):
    """ Calls the QStation's 'save_lights' function """
    # NOTE: I cannot determine a functional difference between this and set_lights; they both
    # seem to set the color/brightness etc of a single bulb (see the description for the 'sn_list'
    # Qstation parameter above in set_lights)
    # Strangely, the example for this function includes a parameter for "angle". I do not know what
    # behavior this is intended to have; setting angle has made no discernible difference in my
    # experience
    cmd = {
        "cmd": "light_ctrl_save",
        "r": color[0],
        "g": color[1],
        "b": color[2],
        "bright": brightness,
        "effect": mode,
        "angle": angle,
        "iswitch": isSwitch,
        "matchValue": matchValue,
        "sn_list": [{"sn": sn} for sn in serials]
    }

    __send_noresp_cmd(cmd)

def send_noresp_cmd(cmd):
    cmd['cmd'] = 'light_ctrl'
    cmd['sn_list'] = [ {"sn": cmd['sn'] }]
    __send_noresp_cmd(cmd)

######### Internal #########

def __send_resp_cmd(cmd, json_response=True):
    """ Sends a command to the QStation that requires waiting for a response """
    """ json_response is a special case for QStation API functions that do not return
        Their result as JSON. ATM the only such command is 'ping' """
    __send_cmd(cmd)
    # Wait for and read in a response and decode it into a utf-8 string
    # TODO: Think about the buffer size here; I'm blindly copy/pasting from the
    # Dheera Belleds API
    resp = sock.recvfrom(1024)[0].decode('utf-8')

    if not json_response:
        return resp

    # Return the response parsed from JSON into a Python dict
    return json.loads(resp)

def __send_noresp_cmd(cmd):
    """ Sends a command to the QStation that will not yield a response """
    __send_cmd(cmd)

def __send_cmd(cmd):
    """ Sends a command to the QStation """
    sock.sendto(json.dumps(cmd).encode('utf-8'), (qstation_address, 11600))
