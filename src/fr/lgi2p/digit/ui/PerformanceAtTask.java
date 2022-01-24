/**
 * 
 */
package fr.lgi2p.digit.ui;

import java.awt.Color; //
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Toolkit;

import javax.swing.JFrame;
import javax.swing.JPanel;

import fr.lgi2p.digit.MainWindow;
import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.conf.Consts;     

import java.util.Locale;

public class PerformanceAtTask {

	private int previousX = 0; 
	private int previousY = 0; 

	private boolean hasReachedThePath = false; 
	private long fistTimeIn = 0;

	// accumulators to incrementally compute effectiveTolerance
	private double radiusSumS = 0;
	private double radiusMean = 0;
	private double effectiveTolerance  = 0; 
	private int nbSample = 0; 

	// accumulators to incrementally compute effectiveTolerance by trial
	private double radiusMeanTable[] = null;	
	private double radiusSumSTable[] = null;	
	private double tolerancesTable[] = null;	

	// effective performance by trial
	private double BeTable[] = null;	
	private double IPeTable[] = null;	
	private double IDeTable[] = null;	
	private double MTeTable[] = null;	
	private String perfText[] = null; 

	// accumulators to incrementally compute effectiveTolerance by trial
	private double angleOutsideTable[] = null;
	private double angleTotalTable[] = null;

	// histogram
	Histogram [] histogramTable = null; 

	private int nbSampleTrial = 0; 

	//    private double radiusStd  = 0; 

	private Configuration configuration = null; 

	private DrawingPanel drawingPanel=null; 



	public PerformanceAtTask(Configuration configuration) {
		Locale.setDefault(Locale.US);

		this.configuration = configuration; 
		setAccululatorsTables();
		setPerformancesTables(); 
		//	setAngleErrorTables();
		setHistogramTable();
		setPerfText(); 

		displayToWindow(); 
	}
	private void setAccululatorsTables() {
		radiusMeanTable = new double[configuration.getCycleMaxNumber()];
		radiusSumSTable = new double[configuration.getCycleMaxNumber()];
		tolerancesTable = new double[configuration.getCycleMaxNumber()];
	}

	private void setPerformancesTables() {
		BeTable = new double[configuration.getCycleMaxNumber()];
		IPeTable  = new double[configuration.getCycleMaxNumber()];
		IDeTable  = new double[configuration.getCycleMaxNumber()];
		MTeTable  = new double[configuration.getCycleMaxNumber()];
		angleTotalTable = new double[configuration.getCycleMaxNumber()];
		angleOutsideTable = new double[configuration.getCycleMaxNumber()];
	}



	private void setHistogramTable() {
		int internalLimit = configuration.getCircularTask().internalLimit; 
		int externalLimit = configuration.getCircularTask().externalLimit; 
		int W = (externalLimit - internalLimit) / 2; 

		int nW = 5 * W; 
		int minLim = internalLimit - nW; 
		int maxLim = externalLimit + nW; 

		int nBins = maxLim - minLim ; 

		histogramTable = new Histogram[configuration.getCycleMaxNumber()]; 
		for(int i=0; i < histogramTable.length ;i++) {
			histogramTable[i] = new Histogram( minLim, maxLim, nBins);
		}
	}

	class DrawingPanel extends JPanel{

		private static final long serialVersionUID = -3247717897935486448L;

		private  Font defaultFont; 

		public Font getFont(){
			return defaultFont; 
		}

		public DrawingPanel() {
			defaultFont = new Font("Courier", Font.PLAIN, 12); 
			setPerfText(); 
		}

		public void paintComponent ( Graphics g ){
			super.paintComponent ( g );

			Color c = g.getColor();
			Font f = g.getFont();

			g.setFont(defaultFont);
			g.setColor(Color.BLACK);

			int fontSize = g.getFont().getSize();
			for (int i = 0; i < perfText.length; i++) {
				g.drawString(perfText[i] , 1, fontSize*(i+1) );
			}

			g.setColor(c);
			g.setFont(f);
		}
	}

	public String  performanceToString(){

		String s = perfText[0]; 

		for (int i = 1; i < perfText.length; i++) {
			s = String.format("%s\n%s", s, perfText[i]); 
		}
		return s;
	}

	public void repaint(){
		setPerfText();
		if (drawingPanel != null) 
			drawingPanel.repaint();
	}

	public String performanceToString(int i) {
		double Te  = getTolerancesTable(i); 
		double Re  = getRadiusMeanTable(i); 
		double MTe = getMTeTable(i); 
		double IPe = getIPeTable(i); 
		double IDe = getIDeTable(i); 
		double Be  = getBeTable(i); 
		double nLaps = angleTotalTable[i] / (2*Math.PI); 
		double MTePerLap = MTe / Math.abs(nLaps);
		double IDePerLap = IDe / Math.abs(nLaps);
		double totAngle = angleTotalTable[i]; 
		double errAngle = angleOutsideTable[i]; 

		double err = 100 * errAngle / totAngle; 

		return String.format(" Rec%03d ,%6.2f ,%8.2f ,%8.2f ,%8.2f ,%8.2f ,%8.2f ,%8.2f ,%8.2f ,", i+1, nLaps, Re, Te, err, MTePerLap, IDePerLap, Be, IPe);

	}

	public void setPerfText(){

		// create header 
		int nLinesHeader = 3; 
		String h[] = new String[nLinesHeader]; 
		h[0]= "   Var: , nLaps ,      Re ,      Te ,  MT/lap , IDe/lap ,      Be ,     IPe ,";
		h[1]= "   unit ,   lap ,   pixel ,   pixel ,   s/lap , bit/lap ,  double ,   bit/s ,";
		h[2]= " Theory ,  1.00 ,  291.50 ,   61.00 ,         ,   30.03 ,    1.00 ,         ,"; 

		h[0]= "    Var , nLaps ,      Re ,      Te ,   error ,  MT/lap , IDe/lap ,      Be ,     IPe ,";
		h[1]= "   unit ,   lap ,   pixel ,   pixel ,       % ,   s/lap , bit/lap ,  double ,   bit/s ,";
		h[2]= " Theory ,  1.00 ,  291.50 ,   61.00 ,    3.88 ,         ,   30.03 ,    1.00 ,         ,"; 

		double R = configuration.getCircularTask().radius; 
		double T = configuration.getCircularTask().tolerance; 
		double ID = configuration.getCircularTask().ID; 
		h[2]= String.format(" Theory ,  1.00 ,%8.2f ,%8.2f ,%8.2f ,    1.00 ,         ,", R, T, ID); 
		h[2]= String.format(" Theory ,  1.00 ,%8.2f ,%8.2f ,    3.88 ,         ,         ,    1.00 ,         ,", R, T, ID); 


		// create perfText
		int nLines = configuration.getCycleMaxNumber()+ nLinesHeader; 
		if (perfText == null) {
			perfText = new String[nLines]; 
		}

		// copy header
		for (int i = 0; i < nLinesHeader; i++) {
			perfText[i] = h[i];
		}
		// copy values 
		for (int i = 0; i < configuration.getCycleMaxNumber(); i++) {
			perfText[i+nLinesHeader]=performanceToString(i) ; 
		}

		//	for (int i = 0; i < perfText.length; i++) {
		//	    System.out.println(perfText[i]);
		//	}

	}



	private void displayToWindow(){	
		JFrame f = new JFrame(Consts.APP_NAME+"DispData");

		drawingPanel = new DrawingPanel(); 
		f.add(drawingPanel);

		// set size to screen width
		Toolkit tk = Toolkit.getDefaultToolkit();  
		int xSize = ((int) tk.getScreenSize().getWidth());  
		int ySize = ((int) tk.getScreenSize().getHeight());  

		int fontSize = drawingPanel.getFont().getSize(); 

		double xSz = perfText[0].length() * fontSize * 0.65  ; 
		double ySz = perfText.length * fontSize * 1.5  ; 
		xSize = (int) Math.round(xSz);
		ySize = (int) Math.round(ySz);
		f.setSize(xSize, ySize);
		f.setVisible(true);

		// give focus to the circular task window
		MainWindow.getInstance(configuration).getFrame().setVisible(true);
		MainWindow.getInstance(configuration).getFrame().setExtendedState(JFrame.MAXIMIZED_BOTH); 	// done AFTER  the content is drawn ?? looks better... indeed

	}

	public void paintHistogramTable(Graphics g, int iHist) {
		histogramTable[iHist].paint(g);
	}


	public void paintHistogram(Graphics g) {

		int iCurrentTrial = MainWindow.getInstance(configuration).NbRecDone - 1; 
		if (iCurrentTrial >= 0 & iCurrentTrial < histogramTable.length ) {
			histogramTable[iCurrentTrial].paint(g);
		} else {
			//histogram.paint(g);
		}
	}


	private void setEffectivePerformance (double radius, int X, int Y ) {
		double currentMean = radius; 
		double currentSumS = 0 ; 
		int currentNbSample = nbSample + 1; 

		currentMean = radiusMean + (radius - radiusMean) / currentNbSample ; 
		currentSumS = radiusSumS + (radius - radiusMean) * (radius - currentMean); 

		radiusMean = currentMean; 
		radiusSumS = currentSumS; 
		double radiusStd  = stdev(currentSumS, currentNbSample); 
		effectiveTolerance = Math.sqrt(2 * Math.PI * Math.E) * radiusStd; 

		nbSample = currentNbSample; 

		//System.out.println( nbSample + ","+ X + "," + Y + "," + radius + "," + radiusMean + "," + radiusSumS + "," + radiusStd);			  

		updateToleranceByTrial(radius); 
	}

	private void updateToleranceByTrial(double radius) {
		double currentMean = radius; 
		double currentSumS = 0 ; 
		int currentNbSample = nbSampleTrial + 1; 

		int currentTrial = MainWindow.getInstance(configuration).NbRecDone - 1; // arrays are indexed to zero

		// update radiusMean and radiusSumS with the novel radius
		double radiusMean = radiusMeanTable[currentTrial]; 
		double radiusSumS = radiusSumSTable[currentTrial]; 

		currentMean = radiusMean + (radius - radiusMean) / currentNbSample ; 
		currentSumS = radiusSumS + (radius - radiusMean) * (radius - currentMean); 

		radiusMean = currentMean; 
		radiusSumS = currentSumS; 

		// compute IDe 
		double radiusStd  = stdev(currentSumS, currentNbSample); 
		double effectiveTolerance = Math.sqrt(2 * Math.PI * Math.E) * radiusStd; 
		double effectiveAngle = angleTotalTable[currentTrial] ;
		double effectiveRadius = radiusMean; 
		double effectiveDistance = Math.abs(effectiveAngle * effectiveRadius); 
		double IDe = effectiveDistance / effectiveTolerance; 

		//double taskRadius = (configuration.getCircularTask().externalLimit + configuration.getCircularTask().internalLimit) / 2.00 ;
		//double IDe = Math.abs(effectiveAngle * taskRadius) / effectiveTolerance; 

		double bias = effectiveTolerance / configuration.getCircularTask().tolerance; 

		// update 
		nbSampleTrial = currentNbSample; 
		radiusMeanTable[currentTrial] = radiusMean; 
		radiusSumSTable[currentTrial] = radiusSumS; 
		tolerancesTable[currentTrial] = effectiveTolerance; 
		BeTable[currentTrial] = bias; 
		IDeTable[currentTrial] = IDe ; 
		IPeTable[currentTrial] = IDe / MTeTable[currentTrial]; 

		// update histogram 
		histogramTable[currentTrial].addValue(radius);

	}

	private double stdev (double SS, int n) {
		// computes the standard deviation from the sum of squares and dof
		if (n < 2) {
			return 0; 
		} else {
			return Math.sqrt(SS / (n - 1));  // stdev uses n-1, not n 
		}
	}


	public void resetHasReachedThePath() {
		nbSampleTrial = 0; 
		hasReachedThePath = false;
	}


	public double getEffectiveTolerance() {
		return effectiveTolerance;
	}

	public double getRadiusMean() {
		return radiusMean;
	}

	public double getTolerancesTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return tolerancesTable[i];
		} else {
			return -1; 
		}
	}

	public double getMTeTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return MTeTable[i];
		} else {
			return -1; 
		}
	}

	public double getIPeTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return IPeTable[i];
		} else {
			return -1; 
		}
	}    

	public double getIDeTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return IDeTable[i];
		} else {
			return -1; 
		}
	}

	public double getBeTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return BeTable[i];
		} else {
			return -1; 
		}
	}

	public double getRadiusMeanTable(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return radiusMeanTable[i];
		} else {
			return -1; 
		}
	}

	public double getReTable(int i ) {
		return getRadiusMeanTable(i ); 
	}

	public double getAngleOutside(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return angleOutsideTable[i];
		} else {
			return -1; 
		}
	}

	public double getAngleTotal(int i ) {
		if (i>=0 & i< configuration.getCycleMaxNumber()) {
			return angleTotalTable[i];
		} else {
			return -1; 
		}
	}

	private double phaseAngle(int cX, int cY, int pX, int pY) {	
		// translate current XY to center of circle 
		int Xc = configuration.getCenterX() - cX; 
		int Yc = configuration.getCenterY() - cY; 
		// translate previous XY to center of circle
		int Xp = configuration.getCenterX() - pX; 
		int Yp = configuration.getCenterY() - pY; 
		// get angles from horizontal 
		double Ac = Math.atan2(Yc, Xc); 
		double Ap = Math.atan2(Yp, Xp); 
		// get the unsigned difference in angle (do not care if moving clockwise or not) 
		double angle = Ap - Ac; 
		double a = angle; 
		// cancel angle jumps around horizontal 
		if (a > Math.PI) {
			angle = angle - 2.0 * Math.PI ; 
		}
		if (a < -Math.PI) {
			angle = angle + 2.0 * Math.PI; 
		}
		//System.out.println(Xc + "," + Yc + "," + Xp + "," + Yp + "," + Ac + "," + Ap  + "," + angle + "," + a ) ; 
		return angle ; 
	}


	private void updateMouse (long time, int X, int Y, boolean isInside, double radius) {
		// double dX = X - previousX; 
		// double dY = Y - previousY; 
		//double euclidianDistance = Math.sqrt(dX*dX + dY*dY);
		double angularDistance = phaseAngle(X, Y, previousX, previousY); 

		int currentTrial = MainWindow.getInstance(configuration).NbRecDone - 1; // arrays are indexed to zero

		if (time > fistTimeIn){
			angleTotalTable[currentTrial] += angularDistance;
			if  ( !isInside) { 
				angleOutsideTable[currentTrial] +=  angularDistance; 
			}
			//System.out.println(time +", "+ X +","+ Y + "," + angularDistance + "," + angleTotalTable[currentTrial] + "," + angleOutsideTable[currentTrial] );
		}

		double MTe = (time - fistTimeIn) ;  
		MTe = MTe / 1000;  			// MT in seconds
		MTeTable[currentTrial] = MTe ; 

		this.setEffectivePerformance(radius, X, Y); 
	}

	public void mouseMoved (long time, int X, int Y, boolean isInside, double radius) {

		// once on the path, start counting 
		if (hasReachedThePath) {
			updateMouse ( time, X,  Y,  isInside,  radius ); 
		} else {
			// still not on the path? do nothing but checking if entering  
			if (isInside & !hasReachedThePath) {	// first time inside
				hasReachedThePath = true; 
				fistTimeIn = time; 
				//System.out.println("fistTimeIn: " + fistTimeIn + "\n" ); 
				updateMouse (time,  X,  Y,  isInside,  radius); 
			}
		}

		// update previous values 
		previousX = X; 
		previousY = Y; 
	}

	class Histogram {

		private double binLim[] = null; 
		private int binVal[] = null; 
		private int nBins = 0; 
		private double minLim = 0; 
		private double maxLim = 0; 

		private int maxHeight = 100; 

		public Histogram(double minLim, double maxLim, int nBins){
			this.nBins = nBins; 
			this.maxLim = maxLim; 
			this.minLim = minLim; 

			double binWidth = (maxLim -minLim) / (double) nBins; 

			binLim = new double[nBins+1]; 
			binVal = new int[nBins]; 

			for(int i = 0; i < binVal.length; i++) {
				binVal[i]=0;
			}
			for(int i = 0; i < binLim.length; i++) {
				binLim[i]=minLim+i*binWidth; 
			}

		}

		public String toString(double [] binLim){
			String s1 = "Lim = ";
			for(int i = 0; i < binLim.length; i++) {
				s1 = String.format("%s%5.2f, ",s1, binLim[i]);
			}
			return s1; 
		}

		public String toString(int [] binVal){
			String s = "Val = ";
			for(int i = 0; i < binVal.length; i++) {
				s = String.format("%s%6d, ",s, binVal[i]);
			}
			return s; 
		}	

		public String toString(){
			String s1 = toString(binLim);	    
			String s2 = toString(binVal);
			return String.format("%s\n%s", s1, s2); 
		}

		public void Print() {
			String s = this.toString();
			String r = String.format("min:%5.2f, max:%5.2f", minLim, maxLim);
			System.out.println(r + "\n" + s); 
		}


		public void addValue (double val) {
			int iBin = -1;
			// find bin where to put the value
			for (int w = 0; w < this.nBins; w++) {
				if (val < binLim[w+1]){
					iBin = w; 
					break; 
				}
			}
			// exclude out of bounds values... 
			if (iBin >=0 & iBin < binVal.length) {
				this.binVal[iBin]++;
			}
		}

		public void paint(Graphics g) {
			int xC = configuration.getCenterX() ;
			int yC = configuration.getCenterY();

			// move to the right part of the circle target q
			//xC = xC + (configuration.getRadiusExternalLimit() + configuration.getRadiusInternalLimit())/2;

			//get maximum value from Histogram and set as maxHeight for plotting
			for (int i = 0; i < nBins; i++) {
				if (maxHeight < binVal[i]) {
					maxHeight = binVal[i];
				}
			}

			// center the histogram along X and Y (with enlargeHeight along Y)
			int shiftX = (nBins/2); 
			int enlargeHeight = 1; 
			int shiftY = (maxHeight/2) * enlargeHeight; 

			// define the top-left coordinate of the histogram to draw
			int x = xC - shiftX; 
			int y = yC - shiftY; 

			// draw the histogram
			g.setColor(Color.green);
			//draw Histogram
			for (int i = 0; i < nBins; i++) {
				g.drawLine(	x+i
						, y + (maxHeight * enlargeHeight)
						, x+i
						, y + (maxHeight - binVal[i]) * enlargeHeight
						);
			}
			// draw the limits of the target 
			g.setColor(Color.white);
			int w = (configuration.getCircularTask().externalLimit - configuration.getCircularTask().internalLimit)/2; 
			//g.drawLine( xC - w, y + (maxHeight * enlargeHeight), xC - w , y); 
			//g.drawLine( xC + w, y + (maxHeight * enlargeHeight), xC + w , y); 

			int width =  10 * maxHeight * enlargeHeight; 
			int height= width; 
			int startAngle = 350; 
			int arcAngle = 20; 
			g.drawArc(xC - w - width
					, y + (maxHeight * enlargeHeight) - height/2
					, width
					, height
					, startAngle
					, arcAngle);

			g.drawArc(xC + w - width
					, y + (maxHeight * enlargeHeight) - height/2
					, width
					, height
					, startAngle
					, arcAngle);

			// draw the corresponding normal distribution : TODO 
		}
	}
}


