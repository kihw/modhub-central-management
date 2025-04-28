import React, { useState, useEffect } from 'react';
import { FaGamepad, FaMoon, FaMusic, FaPlus, FaCog, FaTrash, FaPlayCircle, FaPauseCircle } from 'react-icons/fa';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Switch } from '../../components/ui/switch';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../../components/ui/tooltip';
import { toast } from '../../components/ui/use-toast';
import { useModsContext } from '../../contexts/ModsContext';

const ModCard = ({ mod, onEdit, onDelete, onToggle }) => {
  const getModIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'gaming': return <FaGamepad className="h-6 w-6" />;
      case 'night': return <FaMoon className="h-6 w-6" />;
      case 'media': return <FaMusic className="h-6 w-6" />;
      default: return <FaCog className="h-6 w-6" />;
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-col h-full">
          <div className={`p-4 flex justify-between items-center ${mod.active ? 'bg-primary/10' : 'bg-muted/50'}`}>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${mod.active ? 'bg-primary/20' : 'bg-muted'}`}>
                {getModIcon(mod.type)}
              </div>
              <div>
                <h3 className="font-semibold text-lg">{mod.name}</h3>
                <p className="text-sm text-muted-foreground">{mod.type} Mod</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={mod.automatic ? "secondary" : "outline"}>
                {mod.automatic ? "Auto" : "Manual"}
              </Badge>
              <Switch 
                checked={mod.active} 
                onCheckedChange={() => onToggle(mod.id)}
                aria-label="Toggle mod"
              />
            </div>
          </div>
          
          <div className="p-4 flex-1">
            <p className="text-sm mb-4">{mod.description}</p>
            
            <div className="text-xs text-muted-foreground mb-4">
              {mod.triggers && (
                <div className="mb-2">
                  <strong>Triggers:</strong> {mod.triggers.join(', ')}
                </div>
              )}
              <div>
                <strong>Last activated:</strong> {mod.lastActivated || 'Never'}
              </div>
            </div>
            
            <div className="flex justify-end gap-2 mt-auto">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="icon" onClick={() => onDelete(mod.id)}>
                      <FaTrash className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Delete Mod</TooltipContent>
                </Tooltip>
                
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="icon" onClick={() => onEdit(mod)}>
                      <FaCog className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Edit Mod</TooltipContent>
                </Tooltip>
                
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => onToggle(mod.id)}
                    >
                      {mod.active ? 
                        <FaPauseCircle className="h-4 w-4" /> : 
                        <FaPlayCircle className="h-4 w-4" />
                      }
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {mod.active ? 'Deactivate' : 'Activate'} Mod
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const ModFormDialog = ({ open, onOpenChange, editMod, onSave }) => {
  const initialModState = {
    id: '',
    name: '',
    type: 'custom',
    description: '',
    automatic: false,
    active: false,
    triggers: [],
    lastActivated: null
  };

  const [mod, setMod] = useState(initialModState);
  const [triggerInput, setTriggerInput] = useState('');

  useEffect(() => {
    if (editMod) {
      setMod(editMod);
    } else {
      setMod(initialModState);
    }
  }, [editMod, open]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setMod({
      ...mod,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSelectChange = (name, value) => {
    setMod({
      ...mod,
      [name]: value
    });
  };

  const addTrigger = () => {
    if (triggerInput.trim()) {
      setMod({
        ...mod,
        triggers: [...mod.triggers, triggerInput.trim()]
      });
      setTriggerInput('');
    }
  };

  const removeTrigger = (index) => {
    setMod({
      ...mod,
      triggers: mod.triggers.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newMod = {
      ...mod,
      id: mod.id || Date.now().toString()
    };
    onSave(newMod);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{editMod ? 'Edit Mod' : 'Create New Mod'}</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Mod Name</Label>
              <Input 
                id="name" 
                name="name" 
                value={mod.name} 
                onChange={handleChange} 
                required 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="type">Mod Type</Label>
              <Select 
                value={mod.type} 
                onValueChange={(value) => handleSelectChange('type', value)}
              >
                <SelectTrigger id="type">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gaming">Gaming</SelectItem>
                  <SelectItem value="night">Night</SelectItem>
                  <SelectItem value="media">Media</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea 
              id="description" 
              name="description" 
              value={mod.description} 
              onChange={handleChange} 
              rows={3} 
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch 
              id="automatic" 
              name="automatic" 
              checked={mod.automatic} 
              onCheckedChange={(checked) => handleSelectChange('automatic', checked)} 
            />
            <Label htmlFor="automatic">Automatic activation</Label>
          </div>
          
          <div className="space-y-2">
            <Label>Triggers (Processes, Times, Events)</Label>
            <div className="flex gap-2">
              <Input 
                value={triggerInput} 
                onChange={(e) => setTriggerInput(e.target.value)} 
                placeholder="Add process name or condition"
              />
              <Button type="button" onClick={addTrigger} size="sm">Add</Button>
            </div>
            
            <div className="flex flex-wrap gap-2 mt-2">
              {mod.triggers.map((trigger, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {trigger}
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    className="h-4 w-4 p-0 hover:bg-transparent"
                    onClick={() => removeTrigger(index)}
                  >
                    ×
                  </Button>
                </Badge>
              ))}
            </div>
          </div>
          
          <DialogFooter>
            <Button type="submit">{editMod ? 'Update' : 'Create'} Mod</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const ModsPage = () => {
  const { mods, addMod, updateMod, deleteMod, toggleMod } = useModsContext();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [currentEditMod, setCurrentEditMod] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  
  const filteredMods = mods.filter(mod => {
    if (activeTab === 'all') return true;
    if (activeTab === 'active') return mod.active;
    return mod.type === activeTab;
  });

  const handleEditMod = (mod) => {
    setCurrentEditMod(mod);
    setOpenDialog(true);
  };

  const handleAddMod = () => {
    setCurrentEditMod(null);
    setOpenDialog(true);
  };

  const handleSaveMod = (modData) => {
    if (currentEditMod) {
      updateMod(modData);
      toast({
        title: "Mod updated",
        description: `${modData.name} has been updated successfully.`
      });
    } else {
      addMod(modData);
      toast({
        title: "Mod created",
        description: `${modData.name} has been created successfully.`
      });
    }
  };

  const handleDeleteMod = (modId) => {
    deleteMod(modId);
    toast({
      title: "Mod deleted",
      description: "The mod has been deleted successfully."
    });
  };

  const handleToggleMod = (modId) => {
    toggleMod(modId);
    const mod = mods.find(m => m.id === modId);
    toast({
      title: mod.active ? "Mod deactivated" : "Mod activated",
      description: `${mod.name} has been ${mod.active ? 'deactivated' : 'activated'}.`
    });
  };

  return (
    <div className="container py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Mods Management</h1>
        <Button onClick={handleAddMod}>
          <FaPlus className="mr-2 h-4 w-4" /> New Mod
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
        <TabsList className="mb-4">
          <TabsTrigger value="all">All Mods</TabsTrigger>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="gaming">Gaming</TabsTrigger>
          <TabsTrigger value="night">Night</TabsTrigger>
          <TabsTrigger value="media">Media</TabsTrigger>
          <TabsTrigger value="custom">Custom</TabsTrigger>
        </TabsList>
      </Tabs>

      {filteredMods.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-xl font-medium mb-2">No mods found</h3>
          <p className="text-muted-foreground mb-6">
            {activeTab === 'all' 
              ? "You haven't created any mods yet." 
              : `No ${activeTab} mods available.`}
          </p>
          <Button onClick={handleAddMod}>Create your first mod</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMods.map(mod => (
            <ModCard 
              key={mod.id} 
              mod={mod} 
              onEdit={handleEditMod}
              onDelete={handleDeleteMod}
              onToggle={handleToggleMod}
            />
          ))}
        </div>
      )}

      <ModFormDialog 
        open={openDialog}
        onOpenChange={setOpenDialog}
        editMod={currentEditMod}
        onSave={handleSaveMod}
      />
    </div>
  );
};

export default ModsPage;