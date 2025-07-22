import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { User, Mail, Lock, UserPlus } from 'lucide-react';

export default function UserForm() {
  const [formState, setFormState] = useState({
    email: props.email || '',
    password: '',
    confirmPassword: '',
    role: props.role || 'Usuario'
  });
  
  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formState.email || !/\S+@\S+\.\S+/.test(formState.email)) {
      newErrors.email = 'Correo electrónico inválido';
    }
    
    if (!formState.password || formState.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }
    
    if (formState.password !== formState.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormState({
      ...formState,
      [name]: value
    });
  };
  
  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    setSubmitting(true);
    
    try {
      // Envía la información del formulario a través de Chainlit
      const result = await callAction({
        name: "register_user",
        payload: {
          email: formState.email,
          password: formState.password,
          role: formState.role
        }
      });
      
      if (result.success) {
        setSubmitSuccess(true);
        // Podemos actualizar el mensaje para el usuario
        sendUserMessage(`✅ Usuario ${formState.email} registrado correctamente`);
      } else {
        setErrors({ form: 'Error al registrar usuario. Inténtalo de nuevo.' });
      }
    } catch (error) {
      setErrors({ form: 'Error al procesar la solicitud' });
    } finally {
      setSubmitting(false);
    }
  };
  
  const selectRole = (role) => {
    setFormState({
      ...formState,
      role
    });
  };
  
  if (submitSuccess) {
    return (
      <Card className="w-full max-w-lg mx-auto">
        <CardContent className="pt-6 text-center">
          <div className="rounded-full bg-green-100 p-3 inline-block mb-4">
            <User className="h-6 w-6 text-green-600" />
          </div>
          <h3 className="text-lg font-medium mb-2">¡Usuario registrado con éxito!</h3>
          <p className="text-sm text-gray-500 mb-4">
            El usuario {formState.email} ha sido registrado correctamente con el rol de {formState.role}.
          </p>
          <Button onClick={deleteElement} className="mt-2">
            Cerrar
          </Button>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center gap-2">
          <UserPlus className="h-5 w-5" />
          Registro de Usuario
        </CardTitle>
      </CardHeader>
      <CardContent>
        {errors.form && (
          <div className="bg-red-50 text-red-600 p-3 rounded-md mb-4 text-sm">
            {errors.form}
          </div>
        )}
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">
              Correo electrónico
            </Label>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none z-10" style={{ paddingLeft: '0.5rem' }}>
                <Mail className="h-5 w-5"/>
              </div>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="correo@ejemplo.com"
                className={`${errors.email ? 'border-red-500' : ''}`}
                value={formState.email}
                style={{ paddingLeft: '2rem' }}
                onChange={handleInputChange}
              />
            </div>
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium">
              Contraseña
            </Label>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" style={{ paddingLeft: '0.5rem' }}>
                <Lock className="h-5 w-5" />
              </div>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="********"
                className={`${errors.password ? 'border-red-500' : ''}`}
                style={{ paddingLeft: '2rem' }}
                value={formState.password}
                onChange={handleInputChange}
              />
            </div>
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-sm font-medium">
              Confirmar contraseña
            </Label>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" style={{ paddingLeft: '0.5rem' }}>
                <Lock className="h-5 w-5" />
              </div>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="********"
                className={`${errors.confirmPassword ? 'border-red-500' : ''}`}
                style={{ paddingLeft: '2rem' }}
                value={formState.confirmPassword}
                onChange={handleInputChange}
              />
            </div>
            {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="role" className="text-sm font-medium">
              Rol del usuario
            </Label>
            <div className="grid grid-cols-3 gap-2">
              <Button 
                type="button" 
                variant={formState.role === 'Admin' ? 'default' : 'outline'}
                className="justify-center"
                onClick={() => selectRole('Admin')}
              >
                Admin
              </Button>
              <Button 
                type="button" 
                variant={formState.role === 'Analista' ? 'default' : 'outline'}
                className="justify-center"
                onClick={() => selectRole('Analista')}
              >
                Analista
              </Button>
              <Button 
                type="button" 
                variant={formState.role === 'Usuario' ? 'default' : 'outline'}
                className="justify-center"
                onClick={() => selectRole('Usuario')}
              >
                Usuario
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={deleteElement}>
          Cancelar
        </Button>
        <Button 
          onClick={handleSubmit} 
          disabled={submitting}
          className="gap-2"
        >
          {submitting ? 'Registrando...' : 'Registrar Usuario'}
        </Button>
      </CardFooter>
    </Card>
  );
} 