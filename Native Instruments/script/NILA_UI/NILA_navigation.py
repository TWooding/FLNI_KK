# Import necessary modules and components
import nihia
from script.device_setup import config, constants
from script.screen_writer import NILA_OLED as oled
import arrangement as arrange
import channels
import device
import midi
import mixer
import transport
import plugins
import ui

# Initialize variables for encoder movement on X and Y axes
xAxis, yAxis = 0, 0

# Define the encoder function that handles various events
def encoder(self, event):
    """
    Handle encoder events for a specific controller.

    Parameters:
        self: The instance of the controller.
        event: The event triggered by the encoder movement.

    Returns:
        None
    """

    # Define a helper function for jogging in different UI contexts
    def jog(amount):
        """
        Perform jogging in the UI.

        Parameters:
            amount: The amount by which to jog.

        Returns:
            None
        """
        ui.jog(amount)
        if ui.getFocused(constants.winName["Mixer"]):
            ui.miDisplayRect(mixer.trackNumber(), mixer.trackNumber() + 7, config.rectMixer)
            ui.setHintMsg(mixer.getTrackName(mixer.trackNumber()))
        elif ui.getFocused(constants.winName["Channel Rack"]):
            ui.crDisplayRect(0, channels.selectedChannel(), 256, 8, config.rectChannel)
            ui.setHintMsg("Channel Rack selection rectangle")

    # Define a helper function for browsing through UI elements
    def browse(action):
        """
        Browse through UI elements.

        Parameters:
            action: The action to perform during browsing.

        Returns:
            None
        """
        if ui.isInPopupMenu():
            ui.down() if action == "next" else ui.up()
        else:
            ui.next() if action == "next" else ui.previous()
            oled.OnIdle(self)
            if config.jog_preview_sound == 1:
                ui.previewBrowserMenuItem()
            elif device.getName() != "Komplete Kontrol DAW - 1":
                oled.OnIdle(self)

    # Handle encoder events based on the data received
    if event.data1 in (
        nihia.buttons.button_list.get("ENCODER_GENERAL"),
        nihia.buttons.button_list.get("ENCODER_VOLUME_SELECTED"),
        nihia.buttons.button_list.get("ENCODER_PAN_SELECTED"),
    ):
        if event.data2 in (
            nihia.buttons.button_list.get("RIGHT"),
            constants.mixer_right,
        ):
            event.handled = True
            if ui.getFocused(constants.winName["Mixer"]):
                jog(1)
            elif ui.getFocused(constants.winName["Channel Rack"]):
                jog(1)
            elif ui.getFocused(constants.winName["Plugin"]):
                ui.down(1)
            elif ui.getFocused(constants.winName["Playlist"]):
                ui.jog(1)
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.verZoom(-1)
            elif ui.getFocused(constants.winName["Browser"]):
                browse("next")
            else:
                ui.down(1)

        elif event.data2 in (
            nihia.buttons.button_list.get("LEFT"),
            constants.mixer_left,
        ):
            event.handled = True
            if ui.getFocused(constants.winName["Mixer"]):
                jog(-1)
            elif ui.getFocused(constants.winName["Channel Rack"]):
                jog(-1)
            elif ui.getFocused(constants.winName["Plugin"]):
                ui.up(1)
            elif ui.getFocused(constants.winName["Playlist"]):
                ui.jog(-1)
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.verZoom(1)
            elif ui.getFocused(constants.winName["Browser"]):
                browse("previous")
            else:
                ui.up(1)

    elif event.data1 == nihia.buttons.button_list.get("ENCODER_BUTTON"):
        event.handled = True
        double_click_status = device.isDoubleClick(nihia.buttons.button_list.get("ENCODER_BUTTON"))

        if ui.getFocused(constants.winName["Mixer"]) or ui.getFocused(constants.winName["Channel Rack"]) or ui.getFocused(
            constants.winName["Plugin"]
        ) or ui.getFocused(constants.winName["Piano Roll"]):
            if double_click_status:
                if ui.isInPopupMenu():
                    ui.enter()
                    ui.setHintMsg("Enter")
                else:
                    transport.globalTransport(midi.FPT_Menu, 4)
                    ui.setHintMsg("Open Menu")
                    mixer.deselectAll()
                    mixer.selectTrack(mixer.trackNumber())
            elif ui.isInPopupMenu():
                ui.enter()
                ui.setHintMsg("Enter")

        elif ui.getFocused(constants.winName["Playlist"]):
            if double_click_status:
                if not ui.isInPopupMenu():
                    arrange.addAutoTimeMarker(mixer.getSongTickPos(), str("Mark"))

        elif ui.getFocused(constants.winName["Browser"]):
            if double_click_status:
                if ui.getFocusedNodeFileType() <= -100:
                    ui.enter()
                    ui.setHintMsg("Enter")
                else:
                    ui.selectBrowserMenuItem()
                    ui.setHintMsg("Open menu")
            elif ui.isInPopupMenu():
                ui.enter()
                ui.setHintMsg("Enter")

        else:
            ui.enter()

    if device.getName() == "Komplete Kontrol DAW - 1":
        yAxis, xAxis = nihia.buttons.button_list.get("ENCODER_Y_S"), nihia.buttons.button_list.get("ENCODER_X_S")
    else:
        yAxis, xAxis = nihia.buttons.button_list.get("ENCODER_Y_A"), nihia.buttons.button_list.get("ENCODER_X_A")

    if event.data1 == xAxis:
        event.handled = True
        if event.data2 == nihia.buttons.button_list.get("RIGHT"):
            if ui.getFocused(constants.winName["Mixer"]):
                ui.right(1) if ui.isInPopupMenu() else jog(8)
            elif ui.getFocused(constants.winName["Channel Rack"]):
                ui.left(1) if ui.isInPopupMenu() else ui.right(1)
            elif ui.getFocused(constants.winName["Plugin"]):
                ui.right(1)
            elif ui.getFocused(constants.winName["Playlist"]):
                arrange.jumpToMarker(1, 0)
            elif ui.getFocused(constants.winName["Browser"]):
                ui.right()
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.right() if ui.isInPopupMenu() else ui.jog(1)
            else:
                ui.right(1)

        elif event.data2 == nihia.buttons.button_list.get("LEFT"):
            if ui.getFocused(constants.winName["Mixer"]):
                ui.left(1) if ui.isInPopupMenu() else jog(-8)
            elif ui.getFocused(constants.winName["Channel Rack"]):
                ui.right(1) if ui.isInPopupMenu() else ui.left(1)
            elif ui.getFocused(constants.winName["Plugin"]):
                ui.left(1)
            elif ui.getFocused(constants.winName["Playlist"]):
                arrange.jumpToMarker(-1, 0)
            elif ui.getFocused(constants.winName["Browser"]):
                ui.left()
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.left() if ui.isInPopupMenu() else ui.jog(-1)
            else:
                ui.left(1)

    if event.data1 == yAxis:
        event.handled = True
        if event.data2 == nihia.buttons.button_list.get("UP"):
            if ui.getFocused(constants.winName["Mixer"]):
                ui.up(1) if ui.isInPopupMenu() else None
            elif ui.getFocused(constants.winName["Channel Rack"]):
                ui.up(1)
                ui.crDisplayRect(0, channels.selectedChannel(), 256, 8, config.rectChannel)
            elif ui.getFocused(constants.winName["Plugin"]):
                plugins.prevPreset(channels.channelNumber(channels.selectedChannel())) if channels.getChannelName(
                    channels.selectedChannel()
                ) in ui.getFocusedFormCaption() else ui.up()
            elif ui.getFocused(constants.winName["Browser"]):
                ui.up() if ui.isInPopupMenu() else ui.previous()
                if config.upDown_preview_sound == 1 and device.getName() != "Komplete Kontrol DAW - 1":
                    ui.previewBrowserMenuItem()
                elif device.getName() != "Komplete Kontrol DAW - 1":
                    oled.OnIdle(self)
            elif ui.getFocused(constants.winName["Playlist"]):
                ui.up()
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.up()

        elif event.data2 == nihia.buttons.button_list.get("DOWN"):
            if ui.getFocused(constants.winName["Mixer"]):
                ui.down(1) if ui.isInPopupMenu() else None
            elif ui.getFocused(constants.winName["Channel Rack"]):
                ui.down(1)
                ui.crDisplayRect(0, channels.selectedChannel(), 256, 8, config.rectChannel)
            elif ui.getFocused(constants.winName["Plugin"]):
                plugins.nextPreset(channels.channelNumber(channels.selectedChannel())) if channels.getChannelName(
                    channels.selectedChannel()
                ) in ui.getFocusedFormCaption() else ui.up()
            elif ui.getFocused(constants.winName["Browser"]):
                ui.down() if ui.isInPopupMenu() else ui.next()
                if config.upDown_preview_sound == 1 and device.getName() != "Komplete Kontrol DAW - 1":
                    ui.previewBrowserMenuItem()
                elif device.getName() != "Komplete Kontrol DAW - 1":
                    oled.OnIdle(self)
            elif ui.getFocused(constants.winName["Piano Roll"]):
                ui.down()

    return