import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Camera, 
  CameraOff, 
  Play, 
  Pause, 
  AlertCircle, 
  CheckCircle2,
  User,
  Car,
  Scan
} from 'lucide-react';
import io from 'socket.io-client';

interface DetectionAlert {
  type: 'license_plate' | 'face' | 'student_id';
  message: string;
  status: 'granted' | 'denied';
  timestamp?: string;
}

interface CameraFeedProps {
  onDetection?: (detection: DetectionAlert) => void;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ onDetection }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [detectionActive, setDetectionActive] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>('');
  const [recentAlerts, setRecentAlerts] = useState<DetectionAlert[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<string>('Disconnected');
  
  const socketRef = useRef<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io('http://localhost:5000', {
      transports: ['websocket']
    });

    socketRef.current.on('connect', () => {
      setIsConnected(true);
      setConnectionStatus('Connected');
      console.log('Connected to backend');
    });

    socketRef.current.on('disconnect', () => {
      setIsConnected(false);
      setConnectionStatus('Disconnected');
      console.log('Disconnected from backend');
    });

    socketRef.current.on('camera_frame', (data: { image: string }) => {
      setCurrentFrame(`data:image/jpeg;base64,${data.image}`);
    });

    socketRef.current.on('detection_alert', (alert: DetectionAlert) => {
      const alertWithTimestamp = {
        ...alert,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setRecentAlerts(prev => [alertWithTimestamp, ...prev.slice(0, 4)]);
      
      if (onDetection) {
        onDetection(alertWithTimestamp);
      }
    });

    socketRef.current.on('new_access_log', (logData: any) => {
      console.log('New access log:', logData);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [onDetection]);

  const startCamera = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/start_camera', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        setCameraActive(true);
        setConnectionStatus('Camera Active');
      } else {
        console.error('Failed to start camera');
        setConnectionStatus('Camera Error');
      }
    } catch (error) {
      console.error('Error starting camera:', error);
      setConnectionStatus('Connection Error');
    }
  };

  const stopCamera = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stop_camera', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        setCameraActive(false);
        setDetectionActive(false);
        setCurrentFrame('');
        setConnectionStatus('Camera Stopped');
      }
    } catch (error) {
      console.error('Error stopping camera:', error);
    }
  };

  const toggleDetection = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/toggle_detection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDetectionActive(data.active);
        setConnectionStatus(data.active ? 'Detection Active' : 'Detection Paused');
      }
    } catch (error) {
      console.error('Error toggling detection:', error);
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'license_plate':
        return <Car className="h-4 w-4" />;
      case 'face':
        return <User className="h-4 w-4" />;
      case 'student_id':
        return <Scan className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'granted' ? 'bg-green-500' : 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Camera Controls */}
      <Card className="border-card-border bg-gradient-card shadow-elevated">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-5 w-5" />
              Live Camera Feed
            </CardTitle>
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-muted-foreground">{connectionStatus}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Control Buttons */}
          <div className="flex gap-2">
            <Button
              onClick={cameraActive ? stopCamera : startCamera}
              variant={cameraActive ? "destructive" : "default"}
              disabled={!isConnected}
              className="flex items-center gap-2"
            >
              {cameraActive ? <CameraOff className="h-4 w-4" /> : <Camera className="h-4 w-4" />}
              {cameraActive ? 'Stop Camera' : 'Start Camera'}
            </Button>
            
            <Button
              onClick={toggleDetection}
              variant={detectionActive ? "secondary" : "default"}
              disabled={!cameraActive}
              className="flex items-center gap-2"
            >
              {detectionActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {detectionActive ? 'Pause Detection' : 'Start Detection'}
            </Button>
          </div>

          {/* Video Feed */}
          <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
            {currentFrame ? (
              <img
                src={currentFrame}
                alt="Live Camera Feed"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                {cameraActive ? (
                  <div className="text-center">
                    <Camera className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Waiting for camera feed...</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <CameraOff className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Camera is off</p>
                  </div>
                )}
              </div>
            )}
            
            {/* Detection Status Overlay */}
            {cameraActive && (
              <div className="absolute top-2 left-2">
                <Badge
                  variant={detectionActive ? "default" : "secondary"}
                  className={`${detectionActive ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}
                >
                  {detectionActive ? 'DETECTING' : 'PAUSED'}
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card className="border-card-border bg-gradient-card shadow-elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Recent Detections
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentAlerts.length > 0 ? (
            <div className="space-y-3">
              {recentAlerts.map((alert, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    alert.status === 'granted'
                      ? 'bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800'
                      : 'bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getAlertIcon(alert.type)}
                      <span className="font-medium">{alert.message}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {alert.status === 'granted' ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                      <span className="text-xs text-muted-foreground">
                        {alert.timestamp}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No recent detections</p>
              <p className="text-sm">Start the camera and detection to see alerts here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CameraFeed;