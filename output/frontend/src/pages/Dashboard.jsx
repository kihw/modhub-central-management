import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box, CircularProgress, Card, CardContent, Button } from '@mui/material';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { useNavigate } from 'react-router-dom';
import { useApiService } from '../services/ApiService';
import { useAuthContext } from '../contexts/AuthContext';
import ServerStatusIndicator from '../components/ServerStatusIndicator';
import TaskList from '../components/TaskList';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const navigate = useNavigate();
  const apiService = useApiService();
  const { user } = useAuthContext();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [recentTasks, setRecentTasks] = useState([]);
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Check server status
        try {
          await apiService.checkStatus();
          setServerStatus('online');
        } catch (error) {
          setServerStatus('offline');
        }

        // Get stats data
        const statsData = await apiService.getStats();
        setStats(statsData);

        // Get recent tasks
        const tasksData = await apiService.getTasks({ limit: 5 });
        setRecentTasks(tasksData.tasks || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
    
    // Set up refresh interval
    const intervalId = setInterval(() => {
      apiService.checkStatus()
        .then(() => setServerStatus('online'))
        .catch(() => setServerStatus('offline'));
    }, 30000); // Check every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [apiService]);

  const chartData = {
    labels: stats?.taskHistory?.dates || [],
    datasets: [
      {
        label: 'Tasks Completed',
        data: stats?.taskHistory?.counts || [],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Task Completion Trend',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Tasks',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Date',
        },
      },
    },
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <ServerStatusIndicator status={serverStatus} />
      </Box>

      <Grid container spacing={3}>
        {/* Stats Summary */}
        <Grid item xs={12} md={12}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'row',
              justifyContent: 'space-around',
            }}
          >
            <StatCard
              title="Total Tasks"
              value={stats?.totalTasks || 0}
              description="All tasks in the system"
            />
            <StatCard
              title="Completed Tasks"
              value={stats?.completedTasks || 0}
              description="Successfully completed tasks"
            />
            <StatCard
              title="Pending Tasks"
              value={stats?.pendingTasks || 0}
              description="Tasks waiting to be processed"
            />
            <StatCard
              title="Failed Tasks"
              value={stats?.failedTasks || 0}
              description="Tasks that encountered errors"
            />
          </Paper>
        </Grid>

        {/* Chart */}
        <Grid item xs={12} md={8}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 360,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Task Activity
            </Typography>
            {stats?.taskHistory?.dates.length > 0 ? (
              <Line data={chartData} options={chartOptions} />
            ) : (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                height="100%"
              >
                <Typography variant="body1" color="textSecondary">
                  No activity data available
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* User Info */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 360,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              User Information
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Username:</strong> {user?.username || 'N/A'}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Email:</strong> {user?.email || 'N/A'}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Role:</strong> {user?.role || 'User'}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Last Login:</strong> {user?.lastLogin ? new Date(user.lastLogin).toLocaleString() : 'N/A'}
              </Typography>
            </Box>
            <Box mt="auto">
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => navigate('/profile')}
              >
                View Profile Settings
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Tasks */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography component="h2" variant="h6" color="primary" gutterBottom>
                Recent Tasks
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => navigate('/tasks')}
              >
                View All
              </Button>
            </Box>
            <TaskList tasks={recentTasks} />
            {recentTasks.length === 0 && (
              <Box py={2} textAlign="center">
                <Typography variant="body1" color="textSecondary">
                  No recent tasks found
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

// Helper component for stats cards
const StatCard = ({ title, value, description }) => (
  <Box
    sx={{
      textAlign: 'center',
      p: 1,
    }}
  >
    <Typography variant="h4" component="div" fontWeight="bold" color="primary">
      {value}
    </Typography>
    <Typography variant="h6" component="div">
      {title}
    </Typography>
    <Typography variant="body2" color="text.secondary">
      {description}
    </Typography>
  </Box>
);

export default Dashboard;