package fr.lgi2p.digit.LSL.simple;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;

import java.util.logging.Logger;
import fr.lgi2p.digit.LSL.LSL;
import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.util.Util;

public class LSLSendData {

	private static final Logger logger = Util.getLogger(LSLSendData.class);

	private LSL.StreamInfo simpleDataInfo = null;

	private LSL.StreamOutlet simpleDataOutlet = null;

	private LSL.StreamInfo stringMarkerInfo = null;
	private LSL.StreamOutlet stringMarkerOutlet = null;

	private LSL.StreamInfo metaDataInfo = null;
	@SuppressWarnings("unused")
	private LSL.StreamOutlet metaDataOutlet = null;

	private float[] data = new float[3];

	public LSLSendData() {
		simpleDataInfo = new LSL.StreamInfo(Consts.APP_NAME+"-DataInfo" , "Data", data.length, 100, LSL.ChannelFormat.float32,
				"mouse");
		simpleDataOutlet = new LSL.StreamOutlet(simpleDataInfo);

		stringMarkerInfo = new LSL.StreamInfo(Consts.APP_NAME+"-MarkerInfo", "Markers", 1, LSL.IRREGULAR_RATE,
				LSL.ChannelFormat.string, "mouse");
		stringMarkerOutlet = new LSL.StreamOutlet(stringMarkerInfo);

		metaDataInfo = new LSL.StreamInfo(Consts.APP_NAME+"-MetaDataInfo", "MetaData", 8, 100, LSL.ChannelFormat.float32, "mouse");

	}

	public void dispose() {
		simpleDataOutlet.close();
		simpleDataInfo.destroy();
		stringMarkerOutlet.close();
		stringMarkerInfo.destroy();
	}

	public void sendSimpleData(float timestamp, float x, float y) {
		data[0] = timestamp;
		data[1] = x;
		data[2] = y;

		simpleDataOutlet.push_sample(data);

		try {
			Thread.sleep(5);
		} catch (InterruptedException e) {
		}
	}

	
	public void sendStringData(String marker) {
		String[] sample = new String[1];
		sample[0] = marker;
		stringMarkerOutlet.push_sample(sample);
		
		
		/// output to console (easier to check) 
		final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
		//final SimpleDateFormat sdf = new SimpleDateFormat("mm ss sss");
		Timestamp timestamp = new Timestamp(System.currentTimeMillis());
		System.out.print(sdf.format(timestamp));
		System.out.print(" LSL string : "+ marker + " \n");

	}

//	public void sendMetaData(Configuration configuration) {
//
//		String[] configurationInfo = configuration.toString().split(",");
//
//		LSL.XMLElement chns = metaDataInfo.desc().append_child("configuration");
//
//		for (int i = 0; i < configurationInfo.length; i++) {
//			String[] configurationKeyValue = configurationInfo[i].split("=");
//			chns.append_child_value(configurationKeyValue[0], configurationKeyValue[1]);
//		}
//
//		//PJE: pouruqoi en boucle ? 
//		// while (true) {
//			try {
//				Thread.sleep(1000);
//			} catch (InterruptedException e) {
//				logger.warning("ERROR :" + e.getLocalizedMessage() );
//			}
//			logger.info("Send Meta Data");
//			metaDataOutlet = new LSL.StreamOutlet(metaDataInfo);
//		// }
//	}

}