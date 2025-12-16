import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserFinancialProfile } from '@/types/financial';

interface AuthContextType {
  user: User | null;
  profile: UserFinancialProfile | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, name: string, password: string) => Promise<boolean>;
  logout: () => void;
  saveProfile: (profile: UserFinancialProfile) => Promise<boolean>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = 'http://localhost:8000/api/v1';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserFinancialProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    const initAuth = async () => {
      const token = localStorage.getItem('nestworth_token');
      
      if (token) {
        try {
          // Verify token and get user info
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser({
              id: userData.id,
              email: userData.email,
              name: userData.name,
              createdAt: new Date().toISOString(), // Backend doesn't return this yet
            });

            // Fetch user's profile if they have one
            try {
              const profileResponse = await fetch(`${API_BASE_URL}/profiles/me`, {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              });
              
              if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                setProfile(profileData);
              }
              // If 404, user doesn't have a profile yet - that's okay
            } catch (error) {
              console.error('Error fetching profile:', error);
            }
          } else {
            // Token is invalid, clear it
            localStorage.removeItem('nestworth_token');
          }
        } catch (error) {
          console.error('Error verifying token:', error);
          localStorage.removeItem('nestworth_token');
        }
      }
      
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  const register = async (email: string, name: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, name, password }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        console.error('Registration error:', error);
        return false;
      }
      
      const data = await response.json();
      
      // Store token
      localStorage.setItem('nestworth_token', data.token);
      
      // Set user
      setUser({
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        createdAt: new Date().toISOString(),
      });
      
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      
      // Store token
      localStorage.setItem('nestworth_token', data.token);
      
      // Set user
      setUser({
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        createdAt: new Date().toISOString(),
      });
      
      // Fetch user's profile if they have one
      try {
        const profileResponse = await fetch(`${API_BASE_URL}/profiles/me`, {
          headers: {
            'Authorization': `Bearer ${data.token}`,
          },
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          setProfile(profileData);
        }
        // If 404, user doesn't have a profile yet - that's okay
      } catch (error) {
        console.error('Error fetching profile after login:', error);
      }
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('nestworth_token');
      
      if (token) {
        // Call logout endpoint
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state regardless of API call success
      setUser(null);
      setProfile(null);
      localStorage.removeItem('nestworth_token');
      localStorage.removeItem('nestworth_profile');
    }
  };

  const saveProfile = async (newProfile: UserFinancialProfile): Promise<boolean> => {
    try {
      const token = localStorage.getItem('nestworth_token');
      
      if (!token) {
        console.error('No authentication token found');
        return false;
      }

      console.log('Sending profile data:', JSON.stringify(newProfile, null, 2));

      const response = await fetch(`${API_BASE_URL}/profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newProfile),
      });
      
      console.log('Profile save response status:', response.status);
      
      if (!response.ok) {
        const error = await response.json();
        console.error('Profile save error response:', error);
        console.error('Response status:', response.status);
        return false;
      }
      
      const savedProfile = await response.json();
      console.log('Profile saved successfully:', savedProfile);
      setProfile(savedProfile);
      
      return true;
    } catch (error) {
      console.error('Profile save exception:', error);
      return false;
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return null; // Or a loading spinner
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        login,
        register,
        logout,
        saveProfile,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}