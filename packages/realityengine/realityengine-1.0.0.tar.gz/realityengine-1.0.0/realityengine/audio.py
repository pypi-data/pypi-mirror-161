import simpleaudio
import playsound


class Sound:
    def __init__(self, file: str):
        """
        Creates a new instance of the `Sound` class.

        Sounds currently only support `.wav` files.
        
        Arguments:
            file : str | The path to the sound file.
        """
        try:
            self.file = file
            self.sound = simpleaudio.WaveObject.from_wave_file(self.file)
            self.obj = None
        except:
            raise FileNotFoundError(file)

    def play(self):
        """
        Plays the sound object and returns the sound.
        """
        try:
            obj = self.sound.play()
            self.obj = obj
            return obj
        except:
            return

    def play_and_wait(self):
        """
        Plays the sound objet and delays execution in the current thread until the sound has finished playing.
        """
        try:
            obj = self.sound.play()
            self.obj = obj
            obj.wait_done()
            return obj
        except:
            return

    def stop(self):
        """
        If the sound is currently playing, then the function will stop the sound.
        """
        if self.obj:
            return self.obj.stop()
        
        return