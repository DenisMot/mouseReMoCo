package fr.lgi2p.digit.output;

import java.awt.event.MouseEvent;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.logging.Logger;

import fr.lgi2p.digit.LSL.LSL;
import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.util.Util;


public class OutputMouse {

	private static final Logger logger = Util.getLogger(OutputMouse.class);

	// CSV  
	private BufferedWriter dataWriter = null;
	private BufferedWriter markerWriter = null;

	// LSL Outlets 
	private boolean isWithLSL = false; 
	private String streamNameLSL = "Mouse"; 
	private LSL.StreamOutlet dataOutlet = null;
	private LSL.StreamOutlet markerOutlet = null;
	private LSL.StreamOutlet numericMarkerOutlet = null; 

	public OutputMouse(Configuration configuration) {		
		try {
			String logDate = timeToString(System.currentTimeMillis()) ;

			// FIRST : check availability of external links (from liblsl*.*)
			isWithLSL = isLSLpresent();
			configuration.setWithLSL(isWithLSL);

			// Record in a CSV file : prepare file header for mouse output 
			File logDataFile = new File("data.csv");
			logger.info("Data File write " + logDataFile.getCanonicalPath());
			dataWriter = new BufferedWriter(new FileWriter(logDataFile));     
			dataWriter.write(configuration.toString() + "\n");
			dataWriter.write(logDate+"\n");
			dataWriter.write("\n");
			dataWriter.write("timestamp,mouseX,mouseY,mouseInTarget\n");
			dataWriter.flush();

			// Record in a CSV file : prepare file header for marker output 
			File logMarkersFile = new File("marker.csv");
			logger.info("Marker File write " + logMarkersFile.getCanonicalPath());
			markerWriter = new BufferedWriter(new FileWriter(logMarkersFile));     
			markerWriter.write(configuration.toString() + "\n");
			markerWriter.write(logDate+"\n");
			markerWriter.write("\n");
			markerWriter.flush();

			// Send with LSL : prepare a stream for mouse output 
			if (isWithLSL) {
				SetDataOutlet(configuration);
				SetMarkerOutlet(configuration);
			} 

		} catch (Exception e) {
			logger.warning("ERROR : " + e.getLocalizedMessage());
		} 
	}

	private boolean isLSLpresent( ){
		boolean withLSL = false; 
		try {
			LSL.StreamInfo info = new LSL.StreamInfo(streamNameLSL,"MoCap",3,100,LSL.ChannelFormat.float32, Consts.APP_NAME);
			info.destroy();
			withLSL = true;
			System.out.println("CSV + LSL output...");
		}
		catch (java.lang.Error error) { 
			// any type of error means that we have problem with LSL
			System.out.println("No LSL library: CSV output only");
			//System.out.println(noLSLLibrary); // a bit too verbose... 
			withLSL = false;
		}
		return withLSL;
	}

	private void SetDataOutlet(Configuration configuration) throws IOException {
		// We make a stream of type MoCap with 3 channels 
		// StreamInfo(name, type, channel_count, nominal_srate, channel_format, source_id)
		LSL.StreamInfo info = new LSL.StreamInfo(streamNameLSL+"Data","MoCap",3,100,LSL.ChannelFormat.float32, Consts.APP_NAME);

		// meta info : channels 
		// https://github.com/sccn/xdf/wiki/MoCap-Meta-Data 
		//	at least label+unit.type
		// https://github.com/labstreaminglayer/App-KinectMocap/blob/master/KinectMocap/KinectMocap.cpp
		// 	marker = tracked joint
		// 	object = tracked object 
		String[] labels  = {"mouseX",	 "mouseY",	    "mouseInTarget"};
		//String[] markers = {"mouse",	 "mouse",	    "mouse"};
		String[] markers = {"none",	     "none",	    "none"}; // refers to no marker
		String[] types   = {"PositionX", "PositionY",	"flag"};
		String[] units   = {"pixels",	 "pixels",	    "boolean"};

		LSL.XMLElement chns = info.desc().append_child("channels");
		for (int k=0;k<labels.length;k++)
			chns.append_child("channel")
			.append_child_value("label", labels[k])		
			.append_child_value("marker",markers[k])
			.append_child_value("type",  types[k])
			.append_child_value("unit",  units[k])
			;
			

		// meta info : acquisition  
		info.desc().append_child("acquisition")
		.append_child_value("manufacturer","EuroMov")
		.append_child_value("software",Consts.APP_NAME)
		.append_child_value("version",Consts.APP_VERSION)
		.append_child_value("task",configuration.getTaskString());

		// meta info : configuration   
		LSL.XMLElement config = info.desc().append_child("configuration");
		String[] configurationInfo = configuration.toString().split(";");
		for (int i = 0; i < configurationInfo.length; i++) {
			String[] configurationKeyValue = configurationInfo[i].split(" ");
			config.append_child_value(configurationKeyValue[0], configurationKeyValue[1]);
			//System.out.println(configurationKeyValue[0] +" = "+ configurationKeyValue[1]);
		}

		// create the stream with all the preceding information
		dataOutlet = new LSL.StreamOutlet(info);
	}
	private void SetMarkerOutlet(Configuration configuration) throws IOException {
		// We make a stream of type Marker 
		// StreamInfo(name, type, channel_count, nominal_srate, channel_format, source_id)
		LSL.StreamInfo info = new LSL.StreamInfo(streamNameLSL+"Markers", "Markers", 1, LSL.IRREGULAR_RATE, LSL.ChannelFormat.string, Consts.APP_NAME+"Markers");
		// create the stream with all the preceding information
		markerOutlet = new LSL.StreamOutlet(info);

		// we make a second stream for sync with numeric makers 
		LSL.StreamInfo infoN = new LSL.StreamInfo(streamNameLSL+"ToNIC", "Markers", 1, LSL.IRREGULAR_RATE, LSL.ChannelFormat.int32, Consts.APP_NAME+"MarkersNumeric");
		numericMarkerOutlet = new LSL.StreamOutlet(infoN);
	}

	public void mouseToString(String eventDescription, MouseEvent mouseEvent) {		
		logger.warning(eventDescription + "\t" + System.currentTimeMillis() + "\t" + mouseEvent.getX() + "\t" + mouseEvent.getY() + "\t");
	}

	private String timeToString(long currentTimeMillisec) {
		final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS Z");
		Timestamp timestamp = new Timestamp(currentTimeMillisec);
		return sdf.format(timestamp);
	}

	public void writeNumericMarker(int number) {

		// if (false) {
		// 	long currentTimeMillisec = System.currentTimeMillis(); 
		// 	String currentTimeTxt = timeToString( currentTimeMillisec) ; 
		// 	System.out.print(currentTimeTxt);
		// 	System.out.print(" Lsl string : NumericMarker = "+ number + " \n");
		// }

		if (isWithLSL) {
			int[] sample = new int[1];
			sample[0] = number;
			numericMarkerOutlet.push_sample(sample);
		}
	}

	public void writeMarker(String marker) {
		long currentTimeMillisec = System.currentTimeMillis(); 
		String currentTimeTxt = timeToString( currentTimeMillisec) ; 

		if (isWithLSL) {
			String[] sample = new String[1];
			sample[0] = marker;
			markerOutlet.push_sample(sample);
		}

		/// output to console (easier to check) 
		System.out.print(currentTimeTxt);
		System.out.print(" Lsl string : "+ marker + " \n");

		// Output to markers.csv 
		try {
			markerWriter.write(currentTimeTxt + "," + currentTimeMillisec + "," + marker + "\n");
		} catch (IOException e) {
			// TODO understand why we need this try catch block
			e.printStackTrace();
		}
	}

	public void writeData(long T, int x, int y, boolean isInside) {
		try {
			float[] data = new float[3];
			data[0] = x; 
			data[1] = y; 
			data[2] = (isInside?1:0); 

			if (isWithLSL) {
				dataOutlet.push_sample(data);
			}

			// tests show that writing occurs about 11ms after the mouseEvent
			// System.out.println(T-System.currentTimeMillis() ); 	    
			dataWriter.write( T + "," + x + "," + y + "," + (isInside?1:0) + "\n");
			dataWriter.flush();

		} catch (IOException e) {
			logger.warning("ERROR : " + e.getLocalizedMessage());
		}
	}

	public void dispose() {
		try {
			dataWriter.close();
			markerWriter.close();
			if (isWithLSL) {
				dataOutlet.close();
				markerOutlet.close();
				numericMarkerOutlet.close();
			}

		} catch (Exception e) {
			logger.warning("ERROR : " + e.getLocalizedMessage());
		}		
	}
}
