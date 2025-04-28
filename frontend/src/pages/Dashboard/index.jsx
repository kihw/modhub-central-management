import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Typography, Spin, notification } from 'antd';
import { ReloadOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { fetchDashboardStats, toggleAutomation } from '../../services/api';
import StatusIndicator from '../../components/StatusIndicator';

const { Title } = Typography;

const Dashboard = () => {
  const [stats, setStats] = useState({
    activeMods: 0,
    totalMods: 0,
    activeRules: 0,
    totalRules: 0,
    automationStatus: false,
    lastRunTime: null,
    systemUptime: '0h 0m',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await fetchDashboardStats();
      setStats(data);
      setLoading(false);
    } catch (error) {
      notification.error({
        message: 'Error loading dashboard',
        description: error.message || 'Failed to fetch dashboard statistics',
      });
      setLoading(false);
    }
  };

  const handleToggleAutomation = async () => {
    try {
      setLoading(true);
      const newStatus = await toggleAutomation(!stats.automationStatus);
      setStats(prev => ({ ...prev, automationStatus: newStatus }));
      notification.success({
        message: `Automation ${newStatus ? 'Started' : 'Stopped'}`,
        description: `Automation service has been ${newStatus ? 'started' : 'stopped'} successfully.`,
      });
    } catch (error) {
      notification.error({
        message: 'Toggle Failed',
        description: error.message || 'Failed to toggle automation status',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header" style={{ marginBottom: 20 }}>
        <Title level={2}>System Dashboard</Title>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadDashboardData}
        >
          Refresh
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Mods"
              value={stats.activeMods}
              suffix={`/ ${stats.totalMods}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Rules"
              value={stats.activeRules}
              suffix={`/ ${stats.totalRules}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="System Uptime"
              value={stats.systemUptime}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Last Automation Run"
              value={stats.lastRunTime ? new Date(stats.lastRunTime).toLocaleString() : 'Never'}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Automation Status" style={{ marginTop: 20 }}>
        <Row align="middle">
          <Col span={12}>
            <StatusIndicator status={stats.automationStatus ? 'active' : 'inactive'} />
            <span style={{ marginLeft: 10 }}>
              {stats.automationStatus ? 'Running' : 'Stopped'}
            </span>
          </Col>
          <Col span={12} style={{ textAlign: 'right' }}>
            <Button
              type="primary"
              danger={stats.automationStatus}
              icon={stats.automationStatus ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={handleToggleAutomation}
            >
              {stats.automationStatus ? 'Stop Automation' : 'Start Automation'}
            </Button>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;