import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import CameraFeed from "@/components/CameraFeed";
import { 
  TrendingUp, Users, Car, AlertCircle, Search, 
  Clock, CheckCircle2, XCircle, Activity, User, Scan,
  RefreshCw, Database, Camera, Play, Square, Upload,
  Eye, Settings, Zap
} from "lucide-react";
import io from "socket.io-client";

interface AccessLog {
  timestamp: string;
  detection_type: string;
  detected_value: string;
  student_id?: string;
  student_name?: string;
  status: string;
  confidence?: number;
  plate?: string;
  name?: string;
  userId?: string;
}

interface Student {
  student_id: string;
  name: string;
  email: string;
  active: boolean;
  plates: string[];
}

interface DetectionAlert {
  type: 'license_plate' | 'face' | 'student_id';
  message: string;
  status: 'granted' | 'denied';
  timestamp?: string;
}

interface CameraStatus {
  camera_active: boolean;
  detection_active: boolean;
  camera_available: boolean;
}

interface DetectionStats {
  total_detections: number;
  granted: number;
  denied: number;
  license_plates: number;
  faces: number;
  student_ids: number;
  hourly_distribution: { [key: string]: number };
}

const AdminDashboard = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [accessLogs, setAccessLogs] = useState<AccessLog[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [realtimeStats, setRealtimeStats] = useState({
    totalEntries: 0,
    uniqueVehicles: 0,
    deniedAccess: 0,
    peakHour: "09:00"
  });
  const [recentAlerts, setRecentAlerts] = useState<DetectionAlert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  // Camera and detection states
  const [cameraStatus, setCameraStatus] = useState<CameraStatus>({
    camera_active: false,
    detection_active: false,
    camera_available: false
  });
  const [cameraFrame, setCameraFrame] = useState<string | null>(null);
  const [detectionStats, setDetectionStats] = useState<DetectionStats>({
    total_detections: 0,
    granted: 0,
    denied: 0,
    license_plates: 0,
    faces: 0,
    student_ids: 0,
    hourly_distribution: {}
  });
  const [isImporting, setIsImporting] = useState(false);

  // Socket.IO connection for real-time updates
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
      setAccessLogs(prev => [logData, ...prev.slice(0, 99)]);
      // Update stats immediately when new log arrives
      setTimeout(() => {
        updateRealtimeStats();
        loadDetectionStats();
      }, 100);
    });

    socket.on('detection_alert', (alert: DetectionAlert) => {
      setRecentAlerts(prev => [alert, ...prev.slice(0, 4)]);
    });
    
    socket.on('camera_frame', (frameData: { image: string }) => {
      setCameraFrame(`data:image/jpeg;base64,${frameData.image}`);
    });

    // Load initial data
    loadAccessLogs();
    loadStudents();
    loadCameraStatus();
    loadDetectionStats();
    
    // Set up periodic updates for real-time statistics
    const statsInterval = setInterval(() => {
      updateRealtimeStats();
      loadDetectionStats();
    }, 5000); // Update every 5 seconds

    return () => {
      socket.disconnect();
      clearInterval(statsInterval);
    };
  }, []);

  // Load access logs from API
  const loadAccessLogs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/access_logs');
      if (response.ok) {
        const logs = await response.json();
        setAccessLogs(logs);
        // Update statistics after loading logs
        setTimeout(() => updateRealtimeStats(), 100);
      }
    } catch (error) {
      console.error('Error loading access logs:', error);
    }
  };

  // Load camera status from API
  const loadCameraStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/camera_status');
      if (response.ok) {
        const status = await response.json();
        setCameraStatus(status);
      }
    } catch (error) {
      console.error('Error loading camera status:', error);
    }
  };

  // Load detection statistics
  const loadDetectionStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/detection_stats');
      if (response.ok) {
        const stats = await response.json();
        setDetectionStats(stats);
      }
    } catch (error) {
      console.error('Error loading detection stats:', error);
    }
  };

  // Camera control functions
  const startCamera = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/start_camera', {
        method: 'POST'
      });
      const result = await response.json();
      if (response.ok) {
        loadCameraStatus();
        console.log('Camera started:', result.message);
      } else {
        console.error('Failed to start camera:', result.message);
      }
    } catch (error) {
      console.error('Error starting camera:', error);
    }
  };

  const stopCamera = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stop_camera', {
        method: 'POST'
      });
      const result = await response.json();
      if (response.ok) {
        setCameraFrame(null);
        loadCameraStatus();
        console.log('Camera stopped:', result.message);
      } else {
        console.error('Failed to stop camera:', result.message);
      }
    } catch (error) {
      console.error('Error stopping camera:', error);
    }
  };

  const toggleDetection = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/toggle_detection', {
        method: 'POST'
      });
      const result = await response.json();
      if (response.ok) {
        loadCameraStatus();
        console.log('Detection toggled:', result.message);
      } else {
        console.error('Failed to toggle detection:', result.message);
      }
    } catch (error) {
      console.error('Error toggling detection:', error);
    }
  };

  const importStudentData = async () => {
    setIsImporting(true);
    try {
      const response = await fetch('http://localhost:5000/api/import_csv', {
        method: 'POST'
      });
      const result = await response.json();
      if (response.ok) {
        console.log('Student data imported:', result.message);
        loadStudents(); // Reload student data
        loadDetectionStats(); // Reload stats
      } else {
        console.error('Failed to import student data:', result.message);
      }
    } catch (error) {
      console.error('Error importing student data:', error);
    } finally {
      setIsImporting(false);
    }
  };
  const loadStudents = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/students');
      if (response.ok) {
        const studentsData = await response.json();
        setStudents(studentsData);
      }
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  // Update realtime statistics
  const updateRealtimeStats = () => {
    const today = new Date().toDateString();
    const todayLogs = accessLogs.filter(log => 
      new Date(log.timestamp).toDateString() === today
    );
    
    // Get unique vehicles from today's logs
    const uniqueVehicles = new Set();
    todayLogs.forEach(log => {
      if (log.detection_type === 'license_plate' && log.detected_value) {
        uniqueVehicles.add(log.detected_value);
      }
    });
    
    // Calculate peak hour
    const hourCounts: { [key: string]: number } = {};
    todayLogs.forEach(log => {
      const hour = new Date(log.timestamp).getHours();
      const hourStr = hour.toString().padStart(2, '0') + ':00';
      hourCounts[hourStr] = (hourCounts[hourStr] || 0) + 1;
    });
    
    let peakHour = "09:00";
    let maxCount = 0;
    Object.entries(hourCounts).forEach(([hour, count]) => {
      const countNumber = count as number;
      if (countNumber > maxCount) {
        maxCount = countNumber;
        peakHour = hour;
      }
    });
    
    setRealtimeStats({
      totalEntries: todayLogs.length,
      uniqueVehicles: uniqueVehicles.size,
      deniedAccess: todayLogs.filter(log => log.status === 'denied').length,
      peakHour: peakHour
    });
  };

  // KPI data with dynamic values from both local and backend stats
  const kpis = [
    { 
      label: "Total Entries Today", 
      value: Math.max(realtimeStats.totalEntries, detectionStats.total_detections).toString(), 
      icon: Activity, 
      color: "text-primary" 
    },
    { 
      label: "Unique Vehicles", 
      value: Math.max(realtimeStats.uniqueVehicles, detectionStats.license_plates).toString(), 
      icon: Car, 
      color: "text-accent" 
    },
    { 
      label: "Denied Access", 
      value: Math.max(realtimeStats.deniedAccess, detectionStats.denied).toString(), 
      icon: XCircle, 
      color: "text-destructive" 
    },
    { 
      label: "Peak Traffic Hour", 
      value: realtimeStats.peakHour, 
      icon: Clock, 
      color: "text-highlight" 
    },
  ];

  // Filter access logs based on search
  const filteredAccessLogs = accessLogs.filter(log => {
    const searchLower = searchQuery.toLowerCase();
    return (
      log.detected_value?.toLowerCase().includes(searchLower) ||
      log.student_name?.toLowerCase().includes(searchLower) ||
      log.student_id?.toLowerCase().includes(searchLower)
    );
  });

  const anomalies = [
    {
      id: 1,
      description: "Unrecognized Vehicle: DL-XX-9999 - 3 attempts in 5 minutes",
      severity: "high" as const,
      time: "10 min ago",
    },
    {
      id: 2,
      description: "Access Attempt by Inactive User: Amit Kumar",
      severity: "medium" as const,
      time: "25 min ago",
    },
  ];

  return (
    <div className="min-h-screen bg-background p-6 relative overflow-hidden">
      {/* Enhanced Floating background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        {/* Rotating wireframe cubes */}
        <div className="absolute top-10 right-10 w-64 h-64 border border-primary/30 rotate-45 animate-[spin_30s_linear_infinite]" />
        <div className="absolute top-20 right-20 w-56 h-56 border border-accent/20 rotate-45 animate-[spin_35s_linear_infinite_reverse]" />
        
        {/* Pulsing circles */}
        <div className="absolute bottom-20 left-20 w-48 h-48 border-2 border-accent/30 rounded-full animate-pulse" />
        <div className="absolute bottom-32 left-32 w-32 h-32 border border-highlight/20 rounded-full animate-[pulse_3s_ease-in-out_infinite]" />
        
        {/* Grid pattern */}
        <div className="absolute top-1/2 left-1/4 w-32 h-32 border border-highlight/20 rotate-12 animate-[spin_25s_linear_infinite_reverse]">
          <div className="absolute inset-4 border border-highlight/15" />
        </div>
        
        {/* Scanning lines */}
        <div className="absolute top-1/3 right-1/3 w-2 h-40 bg-gradient-to-b from-transparent via-primary/30 to-transparent animate-[scan_4s_ease-in-out_infinite]" />
        <div className="absolute bottom-1/4 right-1/4 w-40 h-2 bg-gradient-to-r from-transparent via-accent/30 to-transparent animate-[scan_5s_ease-in-out_infinite]" />
        
        {/* Hexagon */}
        <div className="absolute top-1/4 left-1/3 w-24 h-24 border border-primary/20 rotate-45 animate-[spin_40s_linear_infinite]">
          <div className="absolute inset-2 border border-primary/15 rotate-45" />
        </div>
        
        {/* Floating orbs */}
        <div className="absolute top-3/4 right-1/3 w-16 h-16 rounded-full bg-gradient-to-br from-accent/10 to-highlight/10 blur-xl animate-[float_6s_ease-in-out_infinite]" />
        <div className="absolute top-1/4 right-1/4 w-20 h-20 rounded-full bg-gradient-to-br from-primary/10 to-accent/10 blur-xl animate-[float_8s_ease-in-out_infinite]" />
      </div>
      <div className="max-w-7xl mx-auto space-y-6 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-muted-foreground">System analytics and user management</p>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpis.map((kpi, index) => (
            <Card key={index} className="border-card-border bg-gradient-card shadow-elevated">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">{kpi.label}</p>
                    <p className="text-3xl font-bold">{kpi.value}</p>
                  </div>
                  <kpi.icon className={`h-10 w-10 ${kpi.color}`} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Live Camera Feed Section */}
        <Card className="border-card-border bg-gradient-card shadow-elevated">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <Camera className="h-6 w-6 text-primary" />
              Live Security Monitoring
              <div className="ml-auto flex items-center gap-2">
                <Badge variant={isConnected ? "default" : "destructive"} className="text-xs">
                  {isConnected ? "Connected" : "Disconnected"}
                </Badge>
                <Badge 
                  variant={cameraStatus.camera_active ? "default" : "secondary"} 
                  className={`text-xs ${cameraStatus.camera_active ? "bg-green-500" : ""}`}
                >
                  {cameraStatus.camera_active ? "Camera Active" : "Camera Inactive"}
                </Badge>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Camera Controls */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Camera Controls</h3>
                  <div className="flex flex-col gap-2">
                    <Button 
                      onClick={startCamera} 
                      disabled={cameraStatus.camera_active}
                      className="flex items-center gap-2"
                    >
                      <Play className="h-4 w-4" />
                      Start Camera
                    </Button>
                    <Button 
                      onClick={stopCamera} 
                      disabled={!cameraStatus.camera_active}
                      variant="destructive"
                      className="flex items-center gap-2"
                    >
                      <Square className="h-4 w-4" />
                      Stop Camera
                    </Button>
                    <Button 
                      onClick={toggleDetection} 
                      disabled={!cameraStatus.camera_active}
                      variant={cameraStatus.detection_active ? "default" : "secondary"}
                      className="flex items-center gap-2"
                    >
                      <Eye className="h-4 w-4" />
                      {cameraStatus.detection_active ? "Stop Detection" : "Start Detection"}
                    </Button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Student Data</h3>
                  <Button 
                    onClick={importStudentData} 
                    disabled={isImporting}
                    className="flex items-center gap-2 w-full"
                  >
                    {isImporting ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                    {isImporting ? "Importing..." : "Import CSV Data"}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    Import student data from Untitled-Sheet1.csv
                  </p>
                </div>
                
                {/* Real-time Stats */}
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Today's Detections</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-muted/30 p-2 rounded">
                      <div className="text-xs text-muted-foreground">Total</div>
                      <div className="font-bold">{detectionStats.total_detections}</div>
                    </div>
                    <div className="bg-green-500/10 p-2 rounded">
                      <div className="text-xs text-muted-foreground">Granted</div>
                      <div className="font-bold text-green-600">{detectionStats.granted}</div>
                    </div>
                    <div className="bg-red-500/10 p-2 rounded">
                      <div className="text-xs text-muted-foreground">Denied</div>
                      <div className="font-bold text-red-600">{detectionStats.denied}</div>
                    </div>
                    <div className="bg-blue-500/10 p-2 rounded">
                      <div className="text-xs text-muted-foreground">Faces</div>
                      <div className="font-bold text-blue-600">{detectionStats.faces}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Live Video Feed */}
              <div className="lg:col-span-2">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Live Video Feed</h3>
                  <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
                    {cameraFrame ? (
                      <img 
                        src={cameraFrame} 
                        alt="Live camera feed" 
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-white/60">
                        <div className="text-center">
                          <Camera className="h-16 w-16 mx-auto mb-4 opacity-50" />
                          <p className="text-lg">Camera Offline</p>
                          <p className="text-sm">
                            {cameraStatus.camera_active ? 
                              "Waiting for video feed..." : 
                              "Start camera to begin monitoring"
                            }
                          </p>
                        </div>
                      </div>
                    )}
                    {/* Detection Status Overlay */}
                    {cameraStatus.detection_active && (
                      <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                        DETECTING
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Recent Detection Alerts */}
                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Recent Detections</h4>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {recentAlerts.length > 0 ? (
                      recentAlerts.map((alert, index) => (
                        <div key={index} className={`p-2 rounded text-sm ${
                          alert.status === 'granted' ? 'bg-green-500/10 border-l-4 border-green-500' : 'bg-red-500/10 border-l-4 border-red-500'
                        }`}>
                          <div className="flex items-center gap-2">
                            {alert.status === 'granted' ? (
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-600" />
                            )}
                            <span className="font-medium capitalize">{alert.type.replace('_', ' ')}</span>
                            <span className="text-xs text-muted-foreground ml-auto">
                              {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : 'Now'}
                            </span>
                          </div>
                          <p className="text-xs mt-1">{alert.message}</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No recent detections
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <Card className="lg:col-span-2 border-card-border bg-gradient-card shadow-elevated">
            <CardHeader>
              <CardTitle>Access Logs & User Management</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="logs" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="logs">Full Access Log</TabsTrigger>
                  <TabsTrigger value="users">User Management</TabsTrigger>
                </TabsList>

                <TabsContent value="logs" className="space-y-4">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search by plate, name, or ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 bg-background/50 border-muted"
                      />
                    </div>
                  </div>

                  <div className="border border-border rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-muted/50 border-b border-border">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-semibold">Timestamp</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold">License Plate</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold">Name</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold">User ID</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {filteredAccessLogs.map((log, index) => (
                            <tr key={index} className="hover:bg-muted/30 transition-colors">
                              <td className="px-4 py-3 text-sm font-mono">{log.timestamp}</td>
                              <td className="px-4 py-3 text-sm font-mono font-semibold">{log.plate || log.detected_value || '-'}</td>
                              <td className="px-4 py-3 text-sm">{log.name || log.student_name || '-'}</td>
                              <td className="px-4 py-3 text-sm font-mono">{log.userId || log.student_id || '-'}</td>
                              <td className="px-4 py-3">
                                <Badge
                                  variant={log.status === "granted" ? "default" : "destructive"}
                                  className={log.status === "granted" ? "bg-accent" : ""}
                                >
                                  {log.status === "granted" ? (
                                    <CheckCircle2 className="h-3 w-3 mr-1" />
                                  ) : (
                                    <XCircle className="h-3 w-3 mr-1" />
                                  )}
                                  {log.status.toUpperCase()}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="users" className="space-y-4">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search students or faculty..."
                        className="pl-10 bg-background/50 border-muted"
                      />
                    </div>
                    <Button className="shadow-glow-primary">
                      <Users className="h-4 w-4 mr-2" />
                      Add User
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <Card className="border-border bg-muted/30">
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between">
                          <div className="space-y-1">
                            <p className="font-semibold">Rohan Sharma</p>
                            <p className="text-sm text-muted-foreground">STU-2025-001 • Student • Active</p>
                            <div className="flex gap-2 mt-2">
                              <Badge variant="outline" className="text-xs">MH-12-AB-1234</Badge>
                              <Badge variant="outline" className="text-xs">MH-12-CD-5678</Badge>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm">Edit</Button>
                            <Button variant="destructive" size="sm">Deactivate</Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Anomalies */}
            <Card className="border-card-border bg-gradient-card shadow-elevated">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  Anomaly Report
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {anomalies.map((anomaly) => (
                  <div
                    key={anomaly.id}
                    className={`p-3 rounded-lg border ${
                      anomaly.severity === "high"
                        ? "bg-destructive/10 border-destructive"
                        : "bg-muted/30 border-border"
                    }`}
                  >
                    <p className="text-sm font-medium">{anomaly.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">{anomaly.time}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Traffic Chart */}
            <Card className="border-card-border bg-gradient-card shadow-elevated">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Traffic Analytics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-end justify-between gap-1">
                  {/* Generate chart data from hourly distribution or use default */}
                  {(() => {
                    const hours = Array.from({ length: 12 }, (_, i) => {
                      const hour = (8 + i).toString().padStart(2, '0') + ':00';
                      return detectionStats.hourly_distribution?.[hour] || Math.floor(Math.random() * 120) + 20;
                    });
                    
                    const maxHeight = Math.max(...hours, 1);
                    
                    return hours.map((height, i) => (
                      <div
                        key={i}
                        className="flex-1 bg-gradient-primary rounded-t opacity-80 hover:opacity-100 transition-opacity relative group"
                        style={{ height: `${(height / maxHeight) * 100}%` }}
                        title={`${8 + i}:00 - ${height} entries`}
                      >
                        <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-1 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                          {height}
                        </div>
                      </div>
                    ));
                  })()}
                </div>
                <div className="flex justify-between text-xs text-muted-foreground mt-2">
                  <span>8:00</span>
                  <span>12:00</span>
                  <span>16:00</span>
                  <span>20:00</span>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-3">
                  Vehicle Entries - Last 12 Hours (Hover for details)
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
