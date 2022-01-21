package fr.lgi2p.digit.ui;

import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.GridBagConstraints;
import java.awt.Insets;
import java.awt.LayoutManager;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.Window;
import java.net.URL;
import java.text.DateFormat;
import java.text.NumberFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRootPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.border.Border;
import javax.swing.plaf.metal.MetalLookAndFeel;

import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.conf.UiConsts;
import fr.lgi2p.digit.util.Args;
import fr.lgi2p.digit.util.Util;

public final class UiUtil {
	
public static void maximizeOnScreen( GraphicsDevice screen, JFrame frame ){
		frame.setUndecorated(true);
	    frame.setLocation(	screen.getDefaultConfiguration().getBounds().x,
							screen.getDefaultConfiguration().getBounds().y  );
	    frame.setExtendedState(frame.getExtendedState() | JFrame.MAXIMIZED_BOTH);
	}

public static int showOnScreen( int screen, JFrame frame )
{
    GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
   
    GraphicsDevice[] gs = ge.getScreenDevices();
	
	

    if( screen > -1 && screen < gs.length )
    {
    	;	// all is OK 
    }
    else if( gs.length > 0 )
    {
        screen = 0; 		// default to main screen 
    }
    else
    {
        throw new RuntimeException( "No Screens Found" );
    }
    
    // fullscreen means all screens are black and not responding
	//gs[screen].setFullScreenWindow( frame );
        
	// manually set  position and size as a function of screen
    frame.setSize(	gs[screen].getDefaultConfiguration().getBounds().width, 
	    			gs[screen].getDefaultConfiguration().getBounds().height
    				);

    frame.setLocation(	gs[screen].getDefaultConfiguration().getBounds().x,
    					gs[screen].getDefaultConfiguration().getBounds().y
    				);
    
//    frame.setSize(150,150);		// to allow for non-maximized 
//    frame.setExtendedState(frame.getExtendedState() | JFrame.MAXIMIZED_BOTH);
    
    //frame.setVisible(true);
    
    return screen;
}


	
	public static Rectangle screen(Window aWindow) {
		aWindow.pack();
		Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
//		Dimension window = aWindow.getSize();
//		if (window.height > screen.height) {
//			window.height = screen.height;
//		}
//		if (window.width > screen.width) {
//			window.width = screen.width;
//		}
//		int xCoord = (screen.width / 2 - window.width / 2);
//		int yCoord = (screen.height / 2 - window.height / 2);
		
		return new Rectangle( 0 , 0 , screen.width , screen.height  );
	}

	public static void centerAndShow(Window aWindow) {
		// note that the order here is important
		aWindow.pack();
		/*
		 * If called from outside the event dispatch thread (as is the case upon
		 * startup, in the launch thread), then in principle this code is not
		 * thread-safe: once pack has been called, the component is realized, and (most)
		 * further work on the component should take place in the event-dispatch thread.
		 *
		 * In practice, it is exceedingly unlikely that this will lead to an error,
		 * since invisible components cannot receive events.
		 */
		Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
		Dimension window = aWindow.getSize();
		// ensure that no parts of aWindow will be off-screen
		if (window.height > screen.height) {
			window.height = screen.height;
		}
		if (window.width > screen.width) {
			window.width = screen.width;
		}
		int xCoord = (screen.width / 2 - window.width / 2);
		int yCoord = (screen.height / 2 - window.height / 2);
		aWindow.setLocation(xCoord, yCoord);

		aWindow.setVisible(true);
	}


	public static void centerOnParentAndShow(Window aWindow) {
		aWindow.pack();

		Dimension parent = aWindow.getParent().getSize();
		Dimension window = aWindow.getSize();
		int xCoord = aWindow.getParent().getLocationOnScreen().x + (parent.width / 2 - window.width / 2);
		int yCoord = aWindow.getParent().getLocationOnScreen().y + (parent.height / 2 - window.height / 2);

		// Ensure that no part of aWindow will be off-screen
		Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
		int xOffScreenExcess = xCoord + window.width - screen.width;
		if (xOffScreenExcess > 0) {
			xCoord = xCoord - xOffScreenExcess;
		}
		if (xCoord < 0) {
			xCoord = 0;
		}
		int yOffScreenExcess = yCoord + window.height - screen.height;
		if (yOffScreenExcess > 0) {
			yCoord = yCoord - yOffScreenExcess;
		}
		if (yCoord < 0) {
			yCoord = 0;
		}

		aWindow.setLocation(xCoord, yCoord);
		aWindow.setVisible(true);
	}


	public static Border getStandardBorder() {
		return BorderFactory.createEmptyBorder(UiConsts.STANDARD_BORDER, UiConsts.STANDARD_BORDER,
				UiConsts.STANDARD_BORDER, UiConsts.STANDARD_BORDER);
	}


	public static String getDialogTitle(String aSpecificDialogName) {
		Args.checkForContent(aSpecificDialogName);
		StringBuilder result = new StringBuilder(Consts.APP_NAME);
		result.append(": ");
		result.append(aSpecificDialogName);
		return result.toString();
	}


	public static JComponent getCommandRow(java.util.List<JComponent> aButtons) {
		equalizeSizes(aButtons);
		JPanel panel = new JPanel();
		LayoutManager layout = new BoxLayout(panel, BoxLayout.X_AXIS);
		panel.setLayout(layout);
		panel.setBorder(BorderFactory.createEmptyBorder(UiConsts.THREE_SPACES, 0, 0, 0));
		panel.add(Box.createHorizontalGlue());
		Iterator<JComponent> buttonsIter = aButtons.iterator();
		while (buttonsIter.hasNext()) {
			panel.add(buttonsIter.next());
			if (buttonsIter.hasNext()) {
				panel.add(Box.createHorizontalStrut(UiConsts.ONE_SPACE));
			}
		}
		return panel;
	}


	public static JComponent getCommandColumn(java.util.List<JComponent> aButtons) {
		equalizeSizes(aButtons);
		JPanel panel = new JPanel();
		LayoutManager layout = new BoxLayout(panel, BoxLayout.Y_AXIS);
		panel.setLayout(layout);
		panel.setBorder(BorderFactory.createEmptyBorder(0, UiConsts.THREE_SPACES, 0, 0));
		// (no for-each is used here, because of the 'not-yet-last' check)
		Iterator<JComponent> buttonsIter = aButtons.iterator();
		while (buttonsIter.hasNext()) {
			panel.add(buttonsIter.next());
			if (buttonsIter.hasNext()) {
				panel.add(Box.createVerticalStrut(UiConsts.ONE_SPACE));
			}
		}
		panel.add(Box.createVerticalGlue());
		return panel;
	}


	public static ImageIcon getImageIcon(String aImageId) {
		if (!aImageId.startsWith(Consts.BACK_SLASH)) {
			throw new IllegalArgumentException("Image identifier does not start with backslash: " + aImageId);
		}
		return fetchImageIcon(aImageId, UiUtil.class);
	}


	public static ImageIcon getImageIcon(String aImageId, Class<?> aClass) {
		if (aImageId.startsWith(Consts.BACK_SLASH)) {
			throw new IllegalArgumentException("Image identifier starts with a backslash: " + aImageId);
		}
		return fetchImageIcon(aImageId, aClass);
	}


	public static final Dimension getDimensionFromPercent(int aPercentWidth, int aPercentHeight) {
		int low = 1;
		int high = 100;
		Args.checkForRange(aPercentWidth, low, high);
		Args.checkForRange(aPercentHeight, low, high);
		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		return calcDimensionFromPercent(screenSize, aPercentWidth, aPercentHeight);
	}

	public static void equalizeSizes(java.util.List<JComponent> aComponents) {
		Dimension targetSize = new Dimension(0, 0);
		for (JComponent comp : aComponents) {
			Dimension compSize = comp.getPreferredSize();
			double width = Math.max(targetSize.getWidth(), compSize.getWidth());
			double height = Math.max(targetSize.getHeight(), compSize.getHeight());
			targetSize.setSize(width, height);
		}
		setSizes(aComponents, targetSize);
	}


	public static JTextField addSimpleEntryField(Container aContainer, String aName, String aInitialValue,
			int aMnemonic, GridBagConstraints aConstraints, String aTooltip) {
		Args.checkForNull(aName);

		JLabel label = new JLabel(aName);
		label.setDisplayedMnemonic(aMnemonic);
		aContainer.add(label, aConstraints);

		JTextField result = new JTextField(UiConsts.SIMPLE_FIELD_WIDTH);
		label.setLabelFor(result);
		result.setToolTipText(aTooltip);
		if (aInitialValue != null) {
			result.setText(aInitialValue);
		}
		aConstraints.gridx = ++aConstraints.gridx;
		if (aConstraints.weightx == 0.0) {
			aConstraints.weightx = 1.0;
		}
		aContainer.add(result, aConstraints);
		return result;
	}


	public static GridBagConstraints getConstraints(int aY, int aX) {
		int low = 0;
		int high = 10;
		Args.checkForRange(aY, low, high);
		Args.checkForRange(aX, low, high);
		GridBagConstraints result = new GridBagConstraints();
		result.gridy = aY;
		result.gridx = aX;
		result.anchor = GridBagConstraints.WEST;
		result.insets = new Insets(0, 0, 0, UiConsts.ONE_SPACE);
		return result;
	}


	public static GridBagConstraints getConstraints(int aY, int aX, int aWidth, int aHeight) {
		int low = 0;
		int high = 10;
		Args.checkForRange(aHeight, low, high);
		Args.checkForRange(aWidth, low, high);
		GridBagConstraints result = getConstraints(aY, aX);
		result.gridheight = aHeight;
		result.gridwidth = aWidth;
		return result;
	}


	public static JLabel addSimpleDisplayField(Container aContainer, String aName, Object aValue,
			GridBagConstraints aConstraints, boolean aWeightOnDisplay) {
		StringBuilder formattedName = new StringBuilder(aName);
		formattedName.append(": ");
		JLabel name = new JLabel(formattedName.toString());
		aContainer.add(name, aConstraints);

		String valueText = (aValue != null ? aValue.toString() : Consts.EMPTY_STRING);
		JLabel value = new JLabel(valueText);
		truncateLabelIfLong(value);
		aConstraints.gridx = ++aConstraints.gridx;
		if (aWeightOnDisplay) {
			aConstraints.weightx = 1.0;
		}
		aContainer.add(value, aConstraints);

		return value;
	}


	public static void addSimpleDisplayFields(Container aContainer, Map<String, String> aNameValuePairs) {
		Set<String> keys = aNameValuePairs.keySet();
		int rowIdx = 0;
		for (String name : keys) {
			String value = aNameValuePairs.get(name);
			if (value == null) {
				value = Consts.EMPTY_STRING;
			}
			UiUtil.addSimpleDisplayField(aContainer, name, value, UiUtil.getConstraints(rowIdx, 0), true);
			++rowIdx;
		}
	}


	public static void addVerticalGridGlue(JPanel aPanel, int aLastRowIdx) {
		GridBagConstraints glueConstraints = UiUtil.getConstraints(aLastRowIdx, 0);
		glueConstraints.weighty = 1.0;
		glueConstraints.fill = GridBagConstraints.VERTICAL;
		aPanel.add(new JLabel(), glueConstraints);
	}


	public static String getLocalizedPercent(Number aNumber) {
		NumberFormat localFormatter = NumberFormat.getPercentInstance();
		localFormatter.setMinimumFractionDigits(2);
		return localFormatter.format(aNumber.doubleValue());
	}


	public static String getLocalizedInteger(Number aNumber) {
		NumberFormat localFormatter = NumberFormat.getNumberInstance();
		return localFormatter.format(aNumber.intValue());
	}


	public static String getLocalizedTime(Date aDate) {
		DateFormat dateFormat = DateFormat.getTimeInstance(DateFormat.SHORT);
		return dateFormat.format(aDate);
	}


	public static void beep() {
		Toolkit.getDefaultToolkit().beep();
	}


	public static JTextArea getStandardTextArea(String aText) {
		Args.checkForContent(aText);
		if (aText.indexOf(Consts.NEW_LINE) != -1) {
			throw new IllegalArgumentException("Must not contain new line characters: " + aText);
		}
		JTextArea result = new JTextArea(aText);
		result.setEditable(false);
		result.setWrapStyleWord(true);
		result.setLineWrap(true);
		result.setMargin(new Insets(0, UiConsts.ONE_SPACE, 0, UiConsts.ONE_SPACE));
		// this is a bit hacky: the desired color is "secondary3", but cannot see how
		// to reference it directly; hence, an element which uses secondary3 is used
		// instead.
		result.setBackground(MetalLookAndFeel.getMenuBackground());

		return result;
	}


	public static JTextArea getStandardTextAreaHardNewLines(String aText) {
		Args.checkForContent(aText);
		JTextArea result = new JTextArea(aText);
		result.setEditable(false);
		result.setMargin(new Insets(0, UiConsts.ONE_SPACE, 0, UiConsts.ONE_SPACE));
		result.setBackground(MetalLookAndFeel.getMenuBackground());
		return result;
	}


	public static void alignAllX(Container aContainer, UiUtil.AlignX aAlignment) {
		java.util.List<Component> components = Arrays.asList(aContainer.getComponents());
		for (Component comp : components) {
			JComponent jcomp = (JComponent) comp;
			jcomp.setAlignmentX(aAlignment.getValue());
		}
	}

	/** Enumeration for horizontal alignment. */
	public enum AlignX {
		LEFT(Component.LEFT_ALIGNMENT), CENTER(Component.CENTER_ALIGNMENT), RIGHT(Component.RIGHT_ALIGNMENT);
		public float getValue() {
			return fValue;
		}

		private final float fValue;

		private AlignX(float aValue) {
			fValue = aValue;
		}
	}

	public static void alignAllY(Container aContainer, UiUtil.AlignY aAlignment) {
		List<Component> components = Arrays.asList(aContainer.getComponents());
		Iterator<Component> compsIter = components.iterator();
		while (compsIter.hasNext()) {
			JComponent comp = (JComponent) compsIter.next();
			comp.setAlignmentY(aAlignment.getValue());
		}
	}

	/** Type-safe enumeration vertical alignment. */
	public enum AlignY {
		TOP(Component.TOP_ALIGNMENT), CENTER(Component.CENTER_ALIGNMENT), BOTTOM(Component.BOTTOM_ALIGNMENT);
		float getValue() {
			return fValue;
		}

		private final float fValue;

		private AlignY(float aValue) {
			fValue = aValue;
		}
	}

	public static void noDefaultButton(JRootPane aRootPane) {
		aRootPane.setDefaultButton(null);
	}


	private static String addSizeToStandardIcon(String aIconName) {
		assert (Util.textHasContent(aIconName));
		StringBuilder result = new StringBuilder(aIconName);
		if (aIconName.startsWith("/toolbar")) {
			result.append("24.gif");
		} else {
			result.append("16.gif");
		}

		return result.toString();
	}

	private static void setSizes(java.util.List<JComponent> aComponents, Dimension aDimension) {
		Iterator<JComponent> compsIter = aComponents.iterator();
		while (compsIter.hasNext()) {
			JComponent comp = (JComponent) compsIter.next();
			comp.setPreferredSize((Dimension) aDimension.clone());
			comp.setMaximumSize((Dimension) aDimension.clone());
		}
	}

	private static Dimension calcDimensionFromPercent(Dimension aSourceDimension, int aPercentWidth,
			int aPercentHeight) {
		int width = aSourceDimension.width * aPercentWidth / 100;
		int height = aSourceDimension.height * aPercentHeight / 100;
		return new Dimension(width, height);
	}

	private static void truncateLabelIfLong(JLabel aLabel) {
		String originalText = aLabel.getText();
		if (originalText.length() > UiConsts.MAX_LABEL_LENGTH) {
			aLabel.setToolTipText(originalText);
			String truncatedText = originalText.substring(0, UiConsts.MAX_LABEL_LENGTH) + Consts.ELLIPSIS;
			aLabel.setText(truncatedText);
		}
	}

	private static ImageIcon fetchImageIcon(String aImageId, Class<?> aClass) {
		String imgLocation = addSizeToStandardIcon(aImageId);
		URL imageURL = aClass.getResource(imgLocation);
		if (imageURL != null) {
			return new ImageIcon(imageURL);
		} else {
			throw new IllegalArgumentException("Cannot retrieve image using id: " + aImageId);
		}
	}


}