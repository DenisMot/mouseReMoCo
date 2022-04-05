package fr.lgi2p.digit;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.logging.Logger;

import javax.swing.ImageIcon;
import javax.swing.JFrame;

import javax.swing.Timer;

import fr.lgi2p.digit.conf.Calibration;

//import fr.lgi2p.digit.LSL.simple.LSLSendData;
import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.output.OutputMouse;
import fr.lgi2p.digit.ui.DisplayTask;
import fr.lgi2p.digit.ui.PerformanceAtTask;
import fr.lgi2p.digit.util.Util;

public final class MainWindow implements MouseMotionListener, MouseListener, KeyListener, ActionListener {

	Calibration calibration;

	static enum CyclingStatus {
		START, STOP, RECORD, PAUSE
	}

	// markers for LSL outlet to NIC
	private int RECORD_MARKER = 111;
	private int PAUSE_MARKER = 100;

	private int previousX = 0;
	private int previousY = 0;

	public PerformanceAtTask performanceAtTask = null;

	private static final Logger logger = Util.getLogger(MainWindow.class);

	private static MainWindow instance = null;

	private Configuration configuration;

	private JFrame frame = null;

	public JFrame getFrame() {
		return frame;
	}

	private boolean recording = false;

	public boolean isRecording() {
		return recording;
	}

	public boolean isCycling() {
		return isCycling;
	}

	public boolean isCycling = false;
	public int NbRecDone = 0;
	public int NbRestDone = 0;

	private Timer timer = null;
	private Timer timerMoveRest = null;
	private Timer Clock = null;

	public int elapsedSeconds = 0;

	private void startClock() {
		int delay = 1000; // 1 second
		Clock = new Timer(delay, this);
		Clock.setDelay(delay);
		Clock.setInitialDelay(delay);
		Clock.setActionCommand("Update clock");
		Clock.start();
	}

	private DisplayTask displayTask = null;

	private OutputMouse outputMouse = null;

	public OutputMouse getOutputMouse() {
		return outputMouse;
	}

	public static MainWindow getInstance(Configuration configuration) {
		if (instance == null) {
			instance = new MainWindow(configuration);
		}
		return instance;
	}

	public static MainWindow getInstance() {
		return instance;
	}

	private MainWindow(Configuration configuration) {
		this.configuration = configuration;
		this.outputMouse = new OutputMouse(configuration);
		macOsSpecification();
	}

	public void buildAndShow() {
		frame = new JFrame(Consts.APP_NAME);
		frame.addKeyListener(this);

		// Create icon , content of frame, etc.
		frame.setIconImage(new ImageIcon("./src/images/logo.png").getImage());

		// frame.setUndecorated(configuration.getFrameUndecorated()); // more screen,
		// but less flexibility to move the widow
		frame.getContentPane().setBackground(configuration.getBackgroundColor());

		// try a smaller window with nothing inside...
		frame.setSize(configuration.getFrameSize().width, configuration.getFrameSize().height / 2);
		// smaller window (to avoid a white frame if undecorated )
		if (configuration.getFrameUndecorated()) {
			int D = 1;
			frame.setSize(configuration.getFrameSize().width - D, configuration.getFrameSize().height);
		}

		// move the frame at the right position and size
		frame.setLocation(configuration.getFrameLocation());

		if (configuration.getTaskString().equals("circular") & configuration.getCircularTask().ID > 1.0) {
			performanceAtTask = new PerformanceAtTask(configuration);
		}

		// build the content (AFTER setting the configuration)
		displayTask = new DisplayTask(configuration);
		frame.getContentPane().add(displayTask);
		frame.setFont(displayTask.getFont());
		startClock();

		// Exit code
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.addWindowListener(new WindowAdapter() {
			@Override
			public void windowClosing(WindowEvent windowEvent) {
				if (performanceAtTask != null) {
					outputMouse.writeMarker("\n" + performanceAtTask.performanceToString());
				}
				dispose(windowEvent);
			}
		});

		if (configuration.getAutoStart() > 0) {
			timer = new Timer(configuration.getAutoStart(), this);
			timer.setInitialDelay(configuration.getAutoStart() * 1000);
			timer.setActionCommand("DoStartCycleTimedSequence");
			timer.start();
			configuration.setStep("0_WAIT_BEFORE_START");
		} else {
			configuration.setStep("1_START"); // "3_PAUSE"
			actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "record"));
		}

		// the next lines seems useless, I should investigate that later.
		frame.setExtendedState(JFrame.MAXIMIZED_BOTH); // done AFTER the content is drawn ?? looks better... indeed
		frame.setVisible(true);

		// we have to wait for the window to be maximized... 
		try {
			Thread.sleep(1000);
		} catch (InterruptedException ex) {
			Thread.currentThread().interrupt();
		}

		configuration.calibration.setScreenCalibration(frame);
		configuration.calibration.toWindow();

		// create a new OutputMouse with the updated configuration
		this.outputMouse = new OutputMouse(configuration);
		// show configuration on teh console 
		configuration.printConfiguration();
	}

	// Controller
	@Override
	public void actionPerformed(ActionEvent actionEvent) {

		if ("Remove text pause".equals(actionEvent.getActionCommand())) {
			state2RemoveText();
		}
		if ("pause".equals(actionEvent.getActionCommand())) {
			DoPause();
		}
		if ("record".equals(actionEvent.getActionCommand())) {
			DoRecord();
		}
		if ("DoCycleChange".equals(actionEvent.getActionCommand())) {
			DoCycleChange();
		}
		if ("DoStartCycleTimedSequence".equals(actionEvent.getActionCommand())) {
			DoStartCycleTimedSequence();
		}
		if ("End pause".equals(actionEvent.getActionCommand())) {
			endPause();
		}
		if ("Update clock".equals(actionEvent.getActionCommand())) {
			UpdateClock();
		}
		if ("DoDisplayConfiguration".equals(actionEvent.getActionCommand())) {
			DoDisplayConfiguration();
		}
		if ("DoToggleDisplayEffectiveTolerance".equals(actionEvent.getActionCommand())) {
			DoToggleDisplayEffectiveTolerance();
		}

	}

	private void UpdateClock() {
		// called by the clock timer
		elapsedSeconds = elapsedSeconds + 1;
		displayTask.repaint();
		if (performanceAtTask != null)
			performanceAtTask.repaint();
	}

	private void endPause() {
		timerMoveRest.stop();
		this.isCycling = false;

		if (!this.recording) {
			configuration.setStep("END_PAUSE");
			timer.stop();
			displayTask.repaint();
		} else {
			logger.info("Ask to end pause but running");
		}

	}

	private void DoStartCycleTimedSequence() {

		timer.stop(); // stop auto start timer (that is no longer useful during a cycle)

		// a CycleDuration is Run+Rest (with Run duration = Rest duration)
		if (this.isCycling) {
			timerMoveRest.stop();
		} else {
			// prepare the cycle timer
			int CycleDuration = configuration.getCycleDuration() * 1000; // in ms
			timerMoveRest = new Timer(CycleDuration, this);
			timerMoveRest.setDelay(CycleDuration);
			timerMoveRest.setActionCommand("DoCycleChange");
		}
		// start the cycling
		timerMoveRest.setInitialDelay(10); // minimal duration = immediate start
		timerMoveRest.start();
		this.isCycling = true;
	}

	private void restartSecondCounter() {
		elapsedSeconds = 0;
		timerMoveRest.setInitialDelay(configuration.getCycleDuration() * 1000);
		timerMoveRest.restart();
	}

	private void DoCycleChange() {
		// when SPACE is pressed, or automatic call by timerMoveRest, it means, either :
		// - start a cycling sequence
		if (!this.isCycling & NbRecDone < configuration.getCycleMaxNumber()
				&& NbRestDone < configuration.getCycleMaxNumber()) {
			outputMouse.writeMarker("DoCycleChange:DoStartCycleTimedSequence");
			actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "DoStartCycleTimedSequence"));
		}

		// once DoStartCycleTimedSequence has been called...
		restartSecondCounter();
		String Message = " RecordDone=" + NbRecDone + " PauseDone=" + NbRestDone + " ToDo="
				+ configuration.getCycleMaxNumber();
		boolean isSequenceDone = (NbRecDone >= configuration.getCycleMaxNumber()
				&& NbRestDone >= configuration.getCycleMaxNumber());

		// - toggle PAUSE-RECORD
		if (!isSequenceDone) {
			if (NbRecDone <= NbRestDone) {
				outputMouse.writeMarker("DoCycleChange:DoRecord" + Message);
				outputMouse.writeNumericMarker(RECORD_MARKER);
				actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "record"));
			} else {
				outputMouse.writeMarker("DoCycleChange:DoPause" + Message);
				outputMouse.writeNumericMarker(PAUSE_MARKER); // marker for sync with external devices reading only
																// integers
				outputMouse.writeData(0L, 0, 0, false); // show the end of a record with an "all zero line" to ease
														// parsing the output file
				actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "pause"));
			}
		}

		// - stop a cycling sequence
		if (isSequenceDone) {
			outputMouse.writeMarker("DoCycleChange:DoEndPause" + Message);
			if (performanceAtTask != null) {
				outputMouse.writeMarker("\n" + performanceAtTask.performanceToString());
			}
			actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "End pause"));
		}
	}

	private void DoDisplayConfiguration() {
		configuration.toWindow();
		;
	}

	private void state2RemoveText() {
		configuration.setStep("2_START_REMOVE_TEXT");
		logger.info("state2RemoveText");
		timer.stop();
		displayTask.repaint();
	}

	private void DoPause() {
		if (this.recording) {
			configuration.setStep("3_PAUSE");
			toggleRecordPause();
			timer.stop();
			displayTask.repaint();
		} else {
			logger.info("Asked to pause, but already in pause");
		}
	}

	private void DoRecord() {
		if (this.recording == false) {
			configuration.setStep("4_RESUME");
			toggleRecordPause();
			displayTask.repaint();
		} else {
			logger.info("Asked to record, but already recording");
		}
	}

	private void toggleRecordPause() {
		if (this.recording) {
			this.NbRestDone = this.NbRestDone + 1;
			frame.removeMouseListener(this);
			frame.removeMouseMotionListener(this);
		} else {
			this.NbRecDone = this.NbRecDone + 1;
			frame.addMouseListener(this);
			frame.addMouseMotionListener(this);
		}
		this.recording = !this.recording;

		// reset in-out counter at each start-stop ? maybe not...
		if (performanceAtTask != null)
			performanceAtTask.resetHasReachedThePath();
	}

	private void mouseMovedOrDragged(MouseEvent mouseEvent) {
		// if the user presses the stylus, then we get a drag, not a move
		// and we must process both cases

		// check if the cursor is inside the circular target
		// inside = no part of the cursor is hitting the walls...

		// mouse events are relative to the window listener
		int X = mouseEvent.getX(); // pixel (from left of panel)
		int Y = mouseEvent.getY(); // pixel (from top of panel)
		long T = mouseEvent.getWhen(); // milliseconds (since January 1, 1970 UTC)

		// tests show that this occurs about 11ms after the mouseEvent
		// System.out.println(T-System.currentTimeMillis() );

		// make event relative to frame (using insets)
		X = X - configuration.getFrameInsets().left;
		Y = Y - configuration.getFrameInsets().top;

		// make event relative to center of circle
		int dx = configuration.getCenterX() - X;
		int dy = configuration.getCenterY() - Y;

		double d = Math.sqrt(dx * dx + dy * dy); // distance from circle center

		// inside means that d is strictly within limits (limits are not touched)
		int externalLimit = configuration.getCircularTask().externalLimit;
		int internalLimit = configuration.getCircularTask().internalLimit;
		boolean isInside = (d < externalLimit & d > internalLimit);

		if (configuration.getTaskString().equals("circular")) {
			if (configuration.getCircularTask().tolerance_px > 0) {
				if (isInside) {
					displayTask.setCursor(configuration.getCursorRecord());
				} else {
					displayTask.setCursor(configuration.getCursorOut());
				}
			}
		}

		// pass the job to output and performance analysis
		if (this.recording) {
			// only if position changed, record and analyze the data
			// this saves about 50% of the output (
			if (X != previousX | Y != previousY) {
				// if (true) {
				previousX = X;
				previousY = Y;
				outputMouse.writeData(T, X, Y, isInside);
				if (performanceAtTask != null)
					performanceAtTask.mouseMoved(T, X, Y, isInside, d);
			}
		}
	}

	public void dispose(WindowEvent windowEvent) {
		outputMouse.dispose();
		windowEvent.getWindow().dispose();
	}

	public void mouseMoved(MouseEvent mouseEvent) {
		logger.info("mouseMoved");
		mouseMovedOrDragged(mouseEvent);
	}

	public void mouseDragged(MouseEvent mouseEvent) {
		logger.info("mouseDragged");
		mouseMovedOrDragged(mouseEvent);
	}

	public void mouseClicked(MouseEvent mouseEvent) {
		logger.info("mouseClicked");
	}

	public void mouseEntered(MouseEvent mouseEvent) {
		logger.info("mouseEntered");
	}

	public void mouseExited(MouseEvent mouseEvent) {
		logger.info("mouseExited");
	}

	public void mousePressed(MouseEvent mouseEvent) {
		logger.info("mousePressed");
	}

	public void mouseReleased(MouseEvent mouseEvent) {
		logger.info("mouseReleased");
	}

	private void DoToggleDisplayEffectiveTolerance() {
		displayTask.toggleDisplayEffectiveToleranceOn();
	}

	@Override
	public void keyPressed(KeyEvent keyEvent) {
		// key pressed depends on keyboard and locale... not funny for the user to type
		// q for z
	}

	@Override
	public void keyTyped(KeyEvent keyEvent) {
		// 2 things to do : forward key pressed to the marker stream + do action
		String message = "KeyTyped=" + (int) keyEvent.getKeyChar() + " ASCI=" + keyEvent.getKeyChar() + " ";

		switch (keyEvent.getKeyChar()) {
			// specific key => perform action + inform
			case ' ':
				outputMouse.writeMarker(message + "DoCycleChange");
				actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "DoCycleChange"));
				break;

			case 'q':
			case 'Q':
				outputMouse.writeMarker(message + "WINDOW_CLOSING");
				frame.dispatchEvent(new WindowEvent(frame, WindowEvent.WINDOW_CLOSING));
				break;

			case 'c':
				outputMouse.writeMarker(message + "DoDisplayConfiguration");
				actionPerformed(new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "DoDisplayConfiguration"));
				break;

			case 'w':
				if (configuration.getTaskString().equals("circular")) {
					actionPerformed(
							new ActionEvent(this, ActionEvent.ACTION_PERFORMED, "DoToggleDisplayEffectiveTolerance"));
				}
				// default => forward key pressed to the marker stream
			default:
				outputMouse.writeMarker(message);
		}
	}

	@Override
	public void keyReleased(KeyEvent arg0) {
	}

	private void macOsSpecification() {
		System.setProperty("apple.eawt.quitStrategy", "CLOSE_ALL_WINDOWS");
	}

}