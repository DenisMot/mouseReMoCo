package fr.lgi2p.digit.output;

import java.io.File;
import javax.sound.sampled.*;

public class SoundPlayer {
    String fname = "playAtRecord.wav"; 
    Clip soundPlayer = null; 
    File audioFile = null; 

    public SoundPlayer() {
        this.audioFile = new File(fname); 

		if(audioFile.exists() && !audioFile.isDirectory()) { 
            System.out.println("playAtRecord.wav found... "); 
			try {
				soundPlayer = AudioSystem.getClip();
				AudioInputStream audioIn = AudioSystem.getAudioInputStream(this.audioFile);
				soundPlayer.open(audioIn);

				System.out.println("playAtRecord.wav is loading... "); 
				double secondsInAudio = (double) soundPlayer.getMicrosecondLength() / 1000000.0; 
				System.out.println("playAtRecord.wav lasts " + secondsInAudio + " seconds"); 
			} catch (Exception e) {
				System.err.println(e.getMessage());
			}
		}
    }

    public void start(){
        if (soundPlayer != null) {
            soundPlayer.setMicrosecondPosition(0); 
            soundPlayer.start(); 
        }
    }

    public void stop(){
        if (soundPlayer != null) {
            soundPlayer.stop();
        }     
    }

    public void resume(){
        if (soundPlayer != null) {
            soundPlayer.start(); 
        }
    }
}
