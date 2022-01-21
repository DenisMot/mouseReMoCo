package fr.lgi2p.digit.ui;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;

import javax.swing.JComponent;

import fr.lgi2p.digit.conf.Configuration;

public class StartText  extends JComponent {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 8769056085510791176L;
	private Configuration configuration;
	
	public StartText(Configuration configuration) {
		this.configuration = configuration;
	}

	public void paintComponent(Graphics g){		
		
		int deltaX = configuration.getExternalRadius() - configuration.getInternalRadius() ;
		
	    g.setFont(new Font("TimesRoman", Font.PLAIN, 150)); 
	    g.setColor(Color.white);
	    g.drawString("  START ", configuration.getCornerX() +  deltaX, configuration.getCornerY() - deltaX );
		
	}
}
