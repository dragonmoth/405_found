import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import CameraFeed from '@/components/CameraFeed';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  Car,
  User,
  Scan,
  RefreshCw,
  Activity
} from 'lucide-react';
import io from 'socket.io-client';

interface AccessLog {
  timestamp: string;
  detection_type: string;
  detected_value: string;
  student_id?: string;
  student_name?: string;
  status: string;
  confidence?: number;
}

interface DetectionAlert {
  type: 'license_plate' | 'face' | 'student_id';
  message: string;
  status: 'granted' | 'denied';
  timestamp?: string;
}

const SecurityMonitoring = () => {
  const [recentLogs, setRecentLogs] = useState<AccessLog[]>([]);
  const [todayStats, setTodayStats] = useState({
    totalDetections: 0,
    accessGranted: 0,
    accessDenied: 0,
    plateDetections: 0,
    faceDetections: 0,
    idScans: 0
  });
  const [isConnected, setIsConnected] = useState(false);
  const [activeAlerts, setActiveAlerts] = useState<DetectionAlert[]>([]);

  useEffect(() => {
    const socket = io('http://localhost:5000');

    socket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to backend');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from backend');
    });

    socket.on('new_access_log', (logData: AccessLog) => {
      setRecentLogs(prev => [logData, ...prev.slice(0, 19)]);
      updateTodayStats(logData);
    });

    socket.on('detection_alert', (alert: DetectionAlert) => {
      const alertWithTimestamp = {
        ...alert,
        timestamp: new Date().toLocaleTimeString()
      };
      setActiveAlerts(prev => [alertWithTimestamp, ...prev.slice(0, 9)]);
    });

    // Load initial data
    loadRecentLogs();
    calculateTodayStats();

    return () => {
      socket.disconnect();
    };
  }, []);

  const loadRecentLogs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/access_logs');
      if (response.ok) {
        const logs = await response.json();
        setRecentLogs(logs.slice(0, 20));
      }
    } catch (error) {
      console.error('Error loading recent logs:', error);
    }
  };

  const calculateTodayStats = () => {
    const today = new Date().toDateString();
    const todayLogs = recentLogs.filter(log => 
      new Date(log.timestamp).toDateString() === today
    );
    
    setTodayStats({
      totalDetections: todayLogs.length,
      accessGranted: todayLogs.filter(log => log.status === 'granted').length,
      accessDenied: todayLogs.filter(log => log.status === 'denied').length,
      plateDetections: todayLogs.filter(log => log.detection_type === 'license_plate').length,
      faceDetections: todayLogs.filter(log => log.detection_type === 'face').length,
      idScans: todayLogs.filter(log => log.detection_type === 'student_id').length
    });
  };

  const updateTodayStats = (newLog: AccessLog) => {
    const today = new Date().toDateString();
    const logDate = new Date(newLog.timestamp).toDateString();
    
    if (logDate === today) {
      setTodayStats(prev => ({
        totalDetections: prev.totalDetections + 1,
        accessGranted: prev.accessGranted + (newLog.status === 'granted' ? 1 : 0),
        accessDenied: prev.accessDenied + (newLog.status === 'denied' ? 1 : 0),
        plateDetections: prev.plateDetections + (newLog.detection_type === 'license_plate' ? 1 : 0),
        faceDetections: prev.faceDetections + (newLog.detection_type === 'face' ? 1 : 0),
        idScans: prev.idScans + (newLog.detection_type === 'student_id' ? 1 : 0)
      }));
    }
  };

  const handleDetection = (detection: DetectionAlert) => {
    setActiveAlerts(prev => [detection, ...prev.slice(0, 9)]);
  };

  const getDetectionIcon = (type: string) => {
    switch (type) {
      case 'license_plate':
        return <Car className="h-4 w-4" />;
      case 'face':
        return <User className="h-4 w-4" />;
      case 'student_id':
        return <Scan className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              Security Monitoring
            </h1>
            <p className="text-muted-foreground">Real-time campus access monitoring and control</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Total Today</p>
                  <p className="text-2xl font-bold">{todayStats.totalDetections}</p>
                </div>
                <Activity className="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Access Granted</p>
                  <p className="text-2xl font-bold text-green-600">{todayStats.accessGranted}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Access Denied</p>
                  <p className="text-2xl font-bold text-red-600">{todayStats.accessDenied}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Plate Detections</p>
                  <p className="text-2xl font-bold">{todayStats.plateDetections}</p>
                </div>
                <Car className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Face Detections</p>
                  <p className="text-2xl font-bold">{todayStats.faceDetections}</p>
                </div>
                <User className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-card-border bg-gradient-card shadow-elevated">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">ID Scans</p>
                  <p className="text-2xl font-bold">{todayStats.idScans}</p>
                </div>
                <Scan className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Feed */}
          <div>
            <CameraFeed onDetection={handleDetection} />
          </div>

          {/* Activity Monitoring */}
          <div className="space-y-6">
            {/* Active Alerts */}
            <Card className="border-card-border bg-gradient-card shadow-elevated">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-500" />
                    Active Alerts
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActiveAlerts([])}
                  >
                    Clear All
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {activeAlerts.length > 0 ? (
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {activeAlerts.map((alert, index) => (
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
                            {getDetectionIcon(alert.type)}
                            <span className="font-medium text-sm">{alert.message}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            {alert.status === 'granted' ? (
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-600" />
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
                    <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No active alerts</p>
                    <p className="text-sm">All systems operating normally</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="border-card-border bg-gradient-card shadow-elevated">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    Recent Activity
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadRecentLogs}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {recentLogs.length > 0 ? (
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {recentLogs.slice(0, 10).map((log, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/30 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          {getDetectionIcon(log.detection_type)}
                          <div>
                            <p className="font-medium text-sm">
                              {log.student_name || 'Unknown'} - {log.detected_value}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatTimestamp(log.timestamp)}
                            </p>
                          </div>
                        </div>
                        <Badge
                          variant={log.status === 'granted' ? 'default' : 'destructive'}
                          className={log.status === 'granted' ? 'bg-green-500' : 'bg-red-500'}
                        >
                          {log.status.toUpperCase()}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No recent activity</p>
                    <p className="text-sm">Activity will appear here as it happens</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityMonitoring;