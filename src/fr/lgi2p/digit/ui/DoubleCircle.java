package fr.lgi2p.digit.ui;


import java.awt.Color;
import java.awt.Cursor;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Point;
import java.util.logging.Logger;

import javax.swing.JComponent;

import fr.lgi2p.digit.MainWindow;
import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.util.Util;

public class DoubleCircle  extends JComponent {

	private static final Logger logger = Util.getLogger(DoubleCircle.class);

	private static final long serialVersionUID = 226525982964421713L;
	private Configuration configuration;

	private int fontSize = 20; 
	private Font defaultFont = new Font("Courier", Font.PLAIN, fontSize); ; 

	private boolean isDisplayEffectiveToleranceOn = false; 


	public boolean isDisplayEffectiveToleranceOn() {
		return isDisplayEffectiveToleranceOn;
	}

	public void toggleDisplayEffectiveToleranceOn() {
		this.isDisplayEffectiveToleranceOn = !isDisplayEffectiveToleranceOn;
	}

	public DoubleCircle(Configuration configuration) {
		this.configuration = configuration;
		// set cursors  
		this.configuration.setCursorRecord();
		this.configuration.setCursorWait();
		setDefaultFont(); 
	}

	private void setDefaultFont() {
		fontSize = configuration.getCenterX()/36; 
		defaultFont = new Font("Courier", Font.PLAIN, fontSize); 
		this.setFont(defaultFont);
	}

	public void paintComponent(Graphics g){		
		//int fontSize = 20; 			// size of font for start/stop message 
		Point PosMessage = new Point(fontSize, fontSize); 	// position of the start/stop message
		Point PosMessageCycle = new Point(configuration.getFrameSize().width - 20, fontSize); 		//  cycle message (on the right) 
		Point PosPercentMessage = new Point(20, configuration.getFrameSize().height - (fontSize*2)); 	// error rate message (on the left) 

		//System.out.println("configuration--Frame insets " + configuration.getFrameInsets()); 

		if ( ( "0_WAIT_BEFORE_START".equals(configuration.getStep())) || ( "3_PAUSE".equals(configuration.getStep() )  ) ) {
			drawPauseMessage( g, PosMessage,  fontSize) ;            
			setCursor(configuration.getCursorWait());
		}

		if ( ("1_START".equals(configuration.getStep() ) ) ||  ("4_RESUME".equals(configuration.getStep() ) ) ){
			drawRecordMessage( g,  PosMessage,  fontSize);
			drawCycleMessage( g,  PosMessageCycle );
			setCursor(configuration.getCursorRecord());
		}

		if ("2_START_REMOVE_TEXT".equals(configuration.getStep() ) ) {
			drawCycleMessage( g,  PosMessageCycle );
		}

		if ("3_PAUSE".equals(configuration.getStep() ) ) {
			drawPauseMessage( g, PosMessage,  fontSize) ;
			drawCycleMessagePause( g,  PosMessageCycle );
			setCursor(configuration.getCursorWait());
		}
		if ("END_PAUSE".equals(configuration.getStep() ) ) {
			drawEndPauseMessage( g, PosMessage,  fontSize) ;
			drawEndCycleMessage( g,  PosMessageCycle );
			setCursor(new Cursor(Cursor.DEFAULT_CURSOR) );
		}

		drawClockMessage(g, PosMessageCycle );
		drawSquare(g); 
		drawTarget(g); 

		// last : should be on first plane
		if (isDisplayEffectiveToleranceOn) {
			drawEffectiveTolerance(g);
			drawPercentMessage(g, PosPercentMessage );


		}

		logger.info("paintComponent " + configuration.getStep());     
		// System.out.print(" paintComponent : "+ configuration.getStep() + " \n");
	}

	private void drawPauseMessage(Graphics g, Point PosMessage, int fontSize) {
		g.setColor(configuration.getBorderColor());
		g.drawString(" ▌▌ In Pause ('q' to quit, 'space' to toggle record/pause)", PosMessage.x, PosMessage.y  );
	}

	private void drawEndPauseMessage(Graphics g, Point PosMessage, int fontSize) {
		g.setColor(configuration.getBorderColor());
		g.drawString(" Session ended ('q' to quit)", PosMessage.x, PosMessage.y  );
	}

	private void drawRecordMessage(Graphics g, Point PosMessage, int fontSize) {
		//g.setFont(new Font("TimesRoman", Font.PLAIN, fontSize)); 
		g.setColor(configuration.getBorderColor());
		g.drawString(" ► Recording ('q' to quit, 'space' to toggle record/pause)", PosMessage.x, PosMessage.y  );
	}

	private void drawTarget(Graphics g ) {
		if (MainWindow.getInstance(configuration).isCycling()) {
			if (MainWindow.getInstance(configuration).isRecording()) {
				showCircularTarget(g);
				hideCenterTarget(g);
			}else{
				hideCircularTarget( g );
				showCenterTarget(g);
			}
		}else{
			if (configuration.getStep() == "END_PAUSE") {
				hideCircularTarget(g);
				hideCenterTarget(g);
			} else {
				showCircularTarget(g);
				hideCenterTarget(g);
			}
		}
	}

	private void hideCircularTarget(Graphics g ) {
		fillCenteredCircle(	g 
				, configuration.getExternalRadius() 
				, configuration.getBackgroundColor()
				);
	}

	// double circle with adjustable border width
	private void showCircularTarget(Graphics g ) {
		// external (largest) circle : border		
		fillCenteredCircle(	g 
				, configuration.getExternalRadius()
				, configuration.getBorderColor()
				);

		// external (largest) circle : center
		fillCenteredCircle(	g 
				, configuration.getExternalRadius() - configuration.getBorderRadius()
				, Util.toColor("gray").darker().darker().darker().darker()
				);

		// internal circle : border
		fillCenteredCircle(	g 
				, configuration.getInternalRadius()
				, configuration.getBorderColor()
				);

		// internal circle : center
		fillCenteredCircle(	g 
				, configuration.getInternalRadius() -configuration.getBorderRadius() 
				, configuration.getBackgroundColor()
				);
	}

	private void hideCenterTarget(Graphics g ) {
		// draw a filled background within the internal target limits
		// NB :  this is not necessary because showCircularTarget will erase it... 
		fillCenteredCircle(	g 
				, configuration.getInternalRadius() - configuration.getBorderRadius() 
				, configuration.getBackgroundColor()
				);
	}

	private void showCenterTarget(Graphics g ) {
		if (configuration.isWithPauseTarget()){
			int CenterTargetRadius = configuration.getInternalRadius() - configuration.getCursorRadius() *2; 
			Color fillColor = Util.toColor("gray").darker().darker().darker().darker();
			Color bordColor = configuration.getBorderColor();   

			fillCenteredCircle( g , CenterTargetRadius, fillColor); 
			drawCenteredCircle( g , CenterTargetRadius, bordColor); 
		}
	}

	private void drawEffectiveTolerance(Graphics g ) {
		if (isDisplayEffectiveToleranceOn) {
			double We;
			double R;
			int currentTrialIndex; 

			// global values 
			We = MainWindow.getInstance(configuration).performanceAtTask.getEffectiveTolerance();
			R = MainWindow.getInstance(configuration).performanceAtTask.getRadiusMean();

			// current trial values 
			currentTrialIndex = MainWindow.getInstance(configuration).NbRecDone - 1;
			We = MainWindow.getInstance(configuration).performanceAtTask.getTolerancesTable(currentTrialIndex);
			R  = MainWindow.getInstance(configuration).performanceAtTask.getRadiusMeanTable(currentTrialIndex);

			// if radius has been initialized with real values
			if (R > 0) {
				// set the limits...
				double Extern = R + We/2; 
				double Intern = R - We/2; 

				// ... add cursorRadius to match the path 
				Extern += configuration.getCursorRadius();
				Intern -= configuration.getCursorRadius();

				// draw 
				drawCenteredCircle( g , (int) Extern, Util.toColor("blue")); 
				drawCenteredCircle( g , (int) Intern, Util.toColor("blue")); 
			}

			// tests to find the center of the circle in pixel
			//drawCenteredCircle( g , (int) 1, Util.toColor("red"));
			//drawCenteredCircle( g , (int) 2, Util.toColor("white"));
			//drawCenteredCircle( g , (int) 4, Util.toColor("yellow"));

			MainWindow.getInstance(configuration).performanceAtTask.paintHistogram(g);

			//System.out.print(" drawEffectiveTolerance : R "+ R + "We" + We + " \n");
		}
	}


	// draw a circle located at the center 
	private void drawCenteredCircle(Graphics g , int radius, Color color) {
		int X = configuration.getCenterX() - radius; 
		int Y = configuration.getCenterY() - radius; 
		g.setColor(color); 
		g.drawOval(X, Y, 2*radius, 2*radius);
	}

	// fill a circle located at the center 
	private void fillCenteredCircle(Graphics g , int radius, Color color) {
		int X = configuration.getCenterX() - radius; 
		int Y = configuration.getCenterY() - radius; 
		g.setColor(color); 
		g.fillOval(X, Y, 2*radius, 2*radius);
	}

	private void drawSquare(Graphics g ) {
		// draw a white square for the photo-diode to see when it is recording 
		// in the bottom right of the full screen
		// PJE 
		// Modification de la taille du carré de 40 à 2*40
		int SquareSize = 2*40; 

		int x = configuration.getFrameSize().width  - SquareSize; 
		int y = configuration.getFrameSize().height - SquareSize;

		y = y - configuration.getFrameInsets().top - configuration.getFrameInsets().bottom;

		if (MainWindow.getInstance(configuration).isRecording()) {
			g.setColor(Util.toColor("white"));      
		}else{
			g.setColor(Util.toColor("black"));  
		}

		g.fillRect(x, y, SquareSize, SquareSize);
	}

	private void drawCycleMessage(Graphics g, Point PosMessageCycle ){
		String s = "Record " +  MainWindow.getInstance(configuration).NbRecDone; 
		g.setColor(configuration.getBorderColor());
		g.drawString(s
				, PosMessageCycle.x  - g.getFontMetrics().stringWidth(s)
				, PosMessageCycle.y 
				);

	}	

	private void drawClockMessage(Graphics g, Point PosMessageCycle ){
		int Ticks = MainWindow.getInstance(configuration).elapsedSeconds; 
		boolean Cycling = MainWindow.getInstance(configuration).isCycling; 

		String s = " "; 	// default value : no clock info
		if (Cycling ) {
			s = (configuration.getCycleDuration() - Ticks) + " s"; 
		}
		g.setColor(configuration.getBorderColor());
		g.drawString(s
				, PosMessageCycle.x  - g.getFontMetrics().stringWidth(s)
				, PosMessageCycle.y  + g.getFontMetrics().getHeight()
				);

	}

	private void drawPercentMessage(Graphics g, Point PosMessagePercent ){
		Font currFont = g.getFont(); 

		g.setFont(new Font("Courier", Font.PLAIN, 16)); 

		drawRadiusMeanTable     (g, PosMessagePercent); 
		drawAdviceMessage       (g, PosMessagePercent); 

		g.setFont(currFont);

	}

	private void drawAdviceMessage(Graphics g, Point PosMessage ){
		int nbLines = configuration.getCycleMaxNumber() + 5; 
		String s = "type 'w' to hide this..."; 
		drawStringShiftedByLineDown(s, g, PosMessage, -nbLines);

	}

	private void drawRadiusMeanTable(Graphics g, Point PosMessagePercent){
		int nbLines = configuration.getCycleMaxNumber() + 5; 

		//String s = "Lap   We  %err   MTe   IDe   IPe   Be |";
		String s = "Lap %err    We   MTe   IDe   IPe   Be |";

		drawStringShiftedByLineDown(s, g, PosMessagePercent, -nbLines+1);

		for (int i = 0; i < configuration.getCycleMaxNumber(); i++) {
			double tolerance = MainWindow.getInstance(configuration).performanceAtTask.getTolerancesTable(i); 
			double MTe = MainWindow.getInstance(configuration).performanceAtTask.getMTeTable(i); 
			double IPe = MainWindow.getInstance(configuration).performanceAtTask.getIPeTable(i); 
			double IDe = MainWindow.getInstance(configuration).performanceAtTask.getIDeTable(i); 
			double Be = MainWindow.getInstance(configuration).performanceAtTask.getBeTable(i); 

			double totAngle = MainWindow.getInstance(configuration).performanceAtTask.getAngleTotal(i); 
			double outAngle = MainWindow.getInstance(configuration).performanceAtTask.getAngleOutside(i); 
			double error = 100 * outAngle / totAngle; 


			s = String.format("%2d %5.1f %5.2f %5.2f %5.2f %5.2f %5.2f|", i+1, error, tolerance, MTe, IDe, IPe, Be);
			drawStringShiftedByLineDown(s, g, PosMessagePercent, -(i+4) );
		}
	}


	private void drawStringShiftedByLineDown(String s, Graphics g, Point PosMessage, int nLines ){
		g.setColor(configuration.getBorderColor());
		g.drawString(s
				, PosMessage.x  //- g.getFontMetrics().stringWidth(s)
				, PosMessage.y  +  g.getFontMetrics().getHeight() * nLines
				);
	}

	private void drawCycleMessagePause(Graphics g, Point PosMessageCycle ){
		String s = "Done "; 
		if (MainWindow.getInstance(configuration).NbRestDone <= configuration.getCycleMaxNumber() ) {
			s = "Rest " +  MainWindow.getInstance(configuration).NbRestDone; 
		} 
		g.setColor(configuration.getBorderColor());
		g.drawString(s	, PosMessageCycle.x  - g.getFontMetrics().stringWidth(s)
				, PosMessageCycle.y );
	}	

	private void drawEndCycleMessage(Graphics g, Point PosMessageCycle ){
		String s = "      "; 
		g.setColor(configuration.getBorderColor());
		g.drawString(s	, PosMessageCycle.x  - g.getFontMetrics().stringWidth(s)
				, PosMessageCycle.y );
	}
}
