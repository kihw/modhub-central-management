import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Spinner, Badge, Form, InputGroup } from 'react-bootstrap';
import { FaDownload, FaSearch, FaInfoCircle, FaStar, FaExclamationTriangle } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { useTranslation } from 'react-i18next';
import { API_URL } from '../config/constants';
import ErrorBoundary from '../components/ErrorBoundary';
import ModDetailModal from '../components/mods/ModDetailModal';
import PageHeader from '../components/layout/PageHeader';
import EmptyState from '../components/common/EmptyState';

const Mods = () => {
  const { t } = useTranslation();
  const [mods, setMods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMod, setSelectedMod] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [installingMod, setInstallingMod] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    const fetchMods = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/mods`);
        setMods(response.data);
        
        // Extract unique categories
        const uniqueCategories = [...new Set(response.data.map(mod => mod.category))].filter(Boolean);
        setCategories(uniqueCategories);
      } catch (err) {
        console.error('Error fetching mods:', err);
        setError(err.message || 'Failed to fetch mods');
        toast.error(t('mods.fetchError'));
      } finally {
        setLoading(false);
      }
    };

    fetchMods();
  }, [t]);

  const handleInstallMod = async (mod) => {
    try {
      setInstallingMod(mod.id);
      await axios.post(`${API_URL}/mods/install`, { modId: mod.id });
      toast.success(t('mods.installSuccess', { name: mod.name }));
      
      // Update mod status in the list
      setMods(mods.map(m => 
        m.id === mod.id ? { ...m, installed: true } : m
      ));
    } catch (err) {
      console.error('Error installing mod:', err);
      toast.error(t('mods.installError', { name: mod.name }));
    } finally {
      setInstallingMod(null);
    }
  };

  const handleUninstallMod = async (mod) => {
    try {
      setInstallingMod(mod.id);
      await axios.post(`${API_URL}/mods/uninstall`, { modId: mod.id });
      toast.success(t('mods.uninstallSuccess', { name: mod.name }));
      
      // Update mod status in the list
      setMods(mods.map(m => 
        m.id === mod.id ? { ...m, installed: false } : m
      ));
    } catch (err) {
      console.error('Error uninstalling mod:', err);
      toast.error(t('mods.uninstallError', { name: mod.name }));
    } finally {
      setInstallingMod(null);
    }
  };

  const handleShowDetails = (mod) => {
    setSelectedMod(mod);
    setShowDetailModal(true);
  };

  const handleCloseDetailModal = () => {
    setShowDetailModal(false);
    setSelectedMod(null);
  };

  const filteredMods = mods.filter(mod => {
    const matchesSearch = mod.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          mod.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || mod.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">{t('common.loading')}</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <div className="text-center p-5 bg-light rounded">
          <FaExclamationTriangle size={50} className="text-danger mb-3" />
          <h3>{t('common.error')}</h3>
          <p>{error}</p>
          <Button 
            variant="primary" 
            onClick={() => window.location.reload()}
          >
            {t('common.retry')}
          </Button>
        </div>
      </Container>
    );
  }

  return (
    <ErrorBoundary>
      <Container fluid className="p-4">
        <PageHeader 
          title={t('mods.title')} 
          subtitle={t('mods.subtitle')} 
          icon={<FaDownload />} 
        />

        <Row className="mb-4">
          <Col md={6} lg={4}>
            <InputGroup>
              <InputGroup.Text>
                <FaSearch />
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder={t('mods.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
          </Col>
          <Col md={4} lg={3}>
            <Form.Select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">{t('mods.allCategories')}</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </Form.Select>
          </Col>
        </Row>

        {filteredMods.length === 0 ? (
          <EmptyState 
            icon={<FaSearch size={40} />}
            message={t('mods.noModsFound')}
            suggestion={t('mods.tryDifferentSearch')}
          />
        ) : (
          <Row xs={1} md={2} lg={3} xl={4} className="g-4">
            {filteredMods.map(mod => (
              <Col key={mod.id}>
                <Card className="h-100 shadow-sm">
                  {mod.imageUrl && (
                    <Card.Img 
                      variant="top" 
                      src={mod.imageUrl} 
                      style={{ height: '150px', objectFit: 'cover' }} 
                    />
                  )}
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <Card.Title>{mod.name}</Card.Title>
                      {mod.category && (
                        <Badge bg="secondary">{mod.category}</Badge>
                      )}
                    </div>
                    <Card.Text className="text-muted small">
                      {mod.description.length > 100 
                        ? `${mod.description.substring(0, 100)}...` 
                        : mod.description}
                    </Card.Text>
                    <div className="d-flex align-items-center mb-3">
                      <FaStar className="text-warning me-1" />
                      <span>{mod.rating || '0.0'}</span>
                      <span className="mx-2">•</span>
                      <small>{mod.downloads || 0} {t('mods.downloads')}</small>
                    </div>
                  </Card.Body>
                  <Card.Footer className="bg-white">
                    <div className="d-flex justify-content-between">
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleShowDetails(mod)}
                      >
                        <FaInfoCircle className="me-1" />
                        {t('common.details')}
                      </Button>
                      {mod.installed ? (
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleUninstallMod(mod)}
                          disabled={installingMod === mod.id}
                        >
                          {installingMod === mod.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            t('mods.uninstall')
                          )}
                        </Button>
                      ) : (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => handleInstallMod(mod)}
                          disabled={installingMod === mod.id}
                        >
                          {installingMod === mod.id ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            <>
                              <FaDownload className="me-1" />
                              {t('mods.install')}
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        )}

        {selectedMod && (
          <ModDetailModal
            show={showDetailModal}
            mod={selectedMod}
            onClose={handleCloseDetailModal}
            onInstall={handleInstallMod}
            onUninstall={handleUninstallMod}
            installing={installingMod === selectedMod.id}
          />
        )}
      </Container>
    </ErrorBoundary>
  );
};

export default Mods;