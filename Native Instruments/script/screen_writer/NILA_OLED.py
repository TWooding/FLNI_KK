from nihia import mixer as mix
from script.device_setup import NILA_core, constants as c, NILA_transform

import channels
import mixer
import plugins
import transport
import ui
import device
import math
import midi

def OnRefresh(self, event):
    """
    Handles the refreshing of the script's state, updating tracks and parameters based on the currently focused window.

    Parameters:
    - self: The instance of the script.
    - event: The event triggering the refresh.
    """
    self.kompleteInstance = None

    if plugins.isValid(channels.selectedChannel()) and plugins.getPluginName(channels.selectedChannel()) == "Komplete Kontrol":
        if self.kompleteInstance != plugins.getParamName(0, channels.selectedChannel()):
            self.kompleteInstance = plugins.getParamName(0, channels.selectedChannel())
            mix.setTrackKompleteInstance(0, self.kompleteInstance)
    else:
        if self.kompleteInstance:
            self.kompleteInstance = ""
            mix.setTrackKompleteInstance(0, "")

    if ui.getFocused(c.winName["Mixer"]):
        for knobNumber in range(8):
            trackNumber = mixer.trackNumber() + knobNumber
            if mixer.trackNumber() <= c.currentUtility - knobNumber and trackNumber != c.currentUtility:
                mix.setTrackExist(knobNumber, 1)
                mix.setTrackName(knobNumber, mixer.getTrackName(trackNumber))
                mix.setTrackVol(knobNumber, str(NILA_transform.VolTodB(mixer.getTrackVolume(mixer.trackNumber() + knobNumber))) + " dB")
                mix.setTrackVolGraph(knobNumber, mixer.getTrackVolume(trackNumber))
                NILA_transform.updatePanMix(trackNumber, knobNumber)
                mix.setTrackSel(0, 1 if trackNumber == c.currentUtility else 0)
            else:
                mix.setTrackExist(knobNumber, 0)

    if ui.getFocused(c.winName["Channel Rack"]):
        for knobNumber in range(8):
            selectedChannel = channels.selectedChannel() + knobNumber
            if channels.channelCount() > knobNumber and selectedChannel < channels.channelCount():
                mix.setTrackExist(knobNumber, 1)
                mix.setTrackName(knobNumber, channels.getChannelName(selectedChannel))
                mix.setTrackVol(knobNumber, f"{round(channels.getChannelVolume(selectedChannel, 1), 1)} dB")
                mix.setTrackVolGraph(knobNumber, channels.getChannelVolume(selectedChannel) / 1.0 * 0.86)
                NILA_transform.updatePanChannel(selectedChannel, knobNumber)
                mix.setTrackSel(0, 0)
            else:
                mix.setTrackExist(knobNumber, 0)

    if ui.getFocused(c.winName["Plugin"]):
        if not mixer.getActiveEffectIndex():
            purge_tracks(1, 7, clear_info=True)
            purge_tracks(1, 7)
            mix.setTrackExist(0, 1)
            mix.setTrackName(0, f"P| {channels.getChannelName(channels.selectedChannel())}")
            mix.setTrackVol(0, f"{round(channels.getChannelVolume(channels.selectedChannel(), 1), 1)} dB")
            mix.setTrackVolGraph(0, channels.getChannelVolume(channels.selectedChannel()) / 1.0 * 0.86)
            NILA_transform.updatePanChannel(channels.selectedChannel(), 0)
            mix.setTrackSel(0, 0)
        else:
            if device.getName() == "Komplete Kontrol DAW - 1":
                track_index, mixer_slot = mixer.getActiveEffectIndex()
                full_plugin_name = plugins.getPluginName(track_index, mixer_slot)
                
                if "Fruity" in full_plugin_name:
                    # Remove the word "Fruity"
                    full_plugin_name = full_plugin_name.replace("Fruity ", "")
                 
                if not NILA_core.seriesCheck():    
                    plugin_name = full_plugin_name[:9]
                else:
                    plugin_name = full_plugin_name
                    
                mix.setTrackExist(0, 1)
                mix.setTrackName(0, plugin_name)
            else:
                track_index, mixer_slot = mixer.getActiveEffectIndex()
                full_plugin_name = plugins.getPluginName(track_index, mixer_slot)
                
                if "Fruity" in full_plugin_name:
                    # Remove the word "Fruity"
                    full_plugin_name = full_plugin_name.replace("Fruity ", "")
                    
                mix.setTrackExist(0, 1)
                mix.setTrackName(0, f"P| Insert: {track_index}")
                mix.setTrackVol(0, full_plugin_name)
                
            useGlobalIndex = False
                    
            if ui.getFocused(c.winName["Effect Plugin"]):
                mix_track_index, mixer_slot = mixer.getActiveEffectIndex()
                track_plugin_id = mixer.getTrackPluginId(mix_track_index, mixer_slot)
                param_count = plugins.getParamCount(mix_track_index, mixer_slot, useGlobalIndex)
                
                if not track_plugin_id == c.last_plugin_name:
                        c.lead_param = 0
                        c.last_plugin_name = track_plugin_id
                        
                # If there are fewer parameters than knobs, set remaining knobs to non-existent
                for knob_number in range(c.actual_param_count + 1, 8 + 1):
                    
                    if c.actual_param_count < 7:
                        purge_tracks(c.actual_param_count + 1, 7)
                        purge_tracks(c.actual_param_count + 1, 7, clear_info=True)
                    
                if param_count > 0:
                    for knob_number in range(1, min(param_count + c.knob_offset, 8)):  # Ensure we don't go beyond the available parameters or knobs
                        
                        param_index = knob_number - c.knob_offset + c.lead_param                        
                        param_index = min(param_index, param_count - 1)
                        param_index = max(param_index, 0)
                                                
                        param_name = plugins.getParamName(param_index, mix_track_index, mixer_slot, useGlobalIndex)
                                                
                        if param_name != "":
                            param_value = plugins.getParamValue(param_index, mix_track_index, mixer_slot, useGlobalIndex)
                            percentage = param_value * 100
                            
                            if not NILA_core.seriesCheck(): 
                                formatted_param_name = param_name
                            else:
                                formatted_param_name = ""

                                for i, char in enumerate(param_name):
                                    if i > 0 and (
                                        (char.isnumeric() and param_name[i - 1].islower()) or
                                        (char.isupper() and param_name[i - 1].islower()) or
                                        (char.isupper() and param_name[i - 1].isnumeric())
                                    ):
                                        formatted_param_name += " "  # Insert space
                                    formatted_param_name += char

                            mix.setTrackExist(knob_number, 2)
                            mix.setTrackSel(0, 1)
                            mix.setTrackName(knob_number, formatted_param_name)
                            mix.setTrackVol(knob_number, "{}%".format(int(percentage)))
                            
                    actual_non_blank_param_count = 0
                    
                    if param_count == 4240:  # Check if the total parameters equal 4240
    
                        for param_index in range(param_count):
                            param_name = plugins.getParamName(param_index, mix_track_index, mixer_slot, useGlobalIndex)

                            if param_name != "":
                                actual_non_blank_param_count += 1

                        c.actual_param_count = actual_non_blank_param_count - c.unused_midi_cc
                    else:
                        c.actual_param_count = param_count
                else:
                    purge_tracks(1, 7)
                    purge_tracks(1, 7, clear_info=True)
                    

                    
            elif ui.getFocused(c.winName["Generator Plugin"]):
                chan_track_index = channels.selectedChannel()
                plugins.getParamCount(chan_track_index, mixer_slot, useGlobalIndex)

    if ui.getFocused(c.winName["Piano Roll"]):
        purge_tracks(1, 7)
        purge_tracks(1, 7, clear_info=True)
        mix.setTrackName(0, str(channels.getChannelName(channels.selectedChannel())))
        NILA_core.setTrackVolConvert(0, f"{round(channels.getChannelVolume(channels.selectedChannel(), 1), 1)} dB")
        NILA_transform.updatePanChannel(channels.selectedChannel(), 0)

    if ui.getFocused(c.winName["Playlist"]):
        mix.setTrackName(0, "Playlist")
        mix.setTrackVolGraph(0, mixer.getTrackVolume(0))

def OnUpdateBeatIndicator(self, Value):
    """
    Updates the beat indicator based on the focused window (e.g., Playlist).

    Parameters:
    - self: The instance of the script.
    - Value: The value associated with the beat indicator event.
    """
    if ui.getFocused(c.winName["Playlist"]):
        timeDisp, currentTime = NILA_core.timeConvert(c.itemDisp, c.itemTime)
        mix.setTrackName(0, "Playlist")
        split_message = ui.getHintMsg()
        split_point1 = ' - '
        split_point2 = ' to '
        split_hint = split_message.partition(split_point1)[2] if split_point1 in split_message.lower() else split_message.partition(split_point2)[2]

        if device.getName() == "Komplete Kontrol DAW - 1":
            mix.setTrackVol(0, f"|{currentTime}")
        else:
            if transport.isPlaying():
                timeDisp = "B:B" if timeDisp == "Beats:Bar" and len(currentTime) >= 5 else timeDisp
                timeDisp = "M:S" if timeDisp == "Min:Sec" and len(currentTime) > 5 else timeDisp
                mix.setTrackVol(0, f"{timeDisp}|{currentTime}")
            else:
                mix.setTrackVol(0, f"{split_hint[:7]}|{currentTime}")
                mix.setTrackVolGraph(0, mixer.getTrackVolume(0))

def OnIdle(self):
    """
    Performs idle tasks based on the currently focused window.
    
    Parameters:
    - self: The instance of the script.
    """
    if ui.getFocused(c.winName["Playlist"]):
        purge_tracks(1, 7)
        purge_tracks(1, 7, clear_info=True)
        mix.setTrackVolGraph(0, mixer.getTrackVolume(0))
        timeDisp, currentTime = NILA_core.timeConvert(c.itemDisp, c.itemTime)
        split_message = ui.getHintMsg()
        split_point1 = ' - '
        split_point2 = ' to '
        split_hint = split_message.partition(split_point1)[2] if split_point1 in split_message.lower() else split_message.partition(split_point2)[2]

        mix.setTrackName(0, "Playlist")
        if not transport.isPlaying() and "Volume" not in split_hint[:7]:
            mix.setTrackVol(0, f"{split_hint[:7]}|{currentTime}")

    if ui.getFocused(c.winName["Browser"]):
        file_type = ui.getFocusedNodeFileType()
        purge_tracks(1, 7)

        if file_type <= -100:
            file_type = "Browser"
        else:
            for key, value in c.FL_node.items():
                file_type = key if ui.getFocusedNodeFileType() == value else file_type

        mix.setTrackName(0, str(file_type))
        mix.setTrackVol(0, ui.getFocusedNodeCaption()[:15])

def purge_tracks(start, end, clear_info=False):
    """
    Removes or clears tracks based on the specified range.

    Parameters:
    - start: The starting track number.
    - end: The ending track number.
    - clear_info: If True, clears information; otherwise, removes tracks.
    """
    for track_index in range(start, end + 1):
        if clear_info:
            mix.setTrackPanGraph(track_index, 0)
            mix.setTrackVolGraph(track_index, 0)
            mix.setTrackSel(0, 0)
            mix.setTrackArm(track_index, 0)
            mix.setTrackSolo(track_index, 0)
            mix.setTrackMute(track_index, 0)
            mix.setTrackName(track_index, c.blankEvent)
            mix.setTrackPan(track_index, c.blankEvent)
            mix.setTrackVol(track_index, c.blankEvent)
        else:
            mix.setTrackExist(track_index, 0)
    mix.setTrackSel(0, 0)