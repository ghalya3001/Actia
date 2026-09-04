import React, { useState } from 'react';
import { LogIn, UserPlus, ShieldAlert, Mail, Lock, User, Send, CheckCircle2, ArrowLeft } from 'lucide-react';

export default function AuthScreen({ onLoginSuccess, showToast }) {
  const [activeTab, setActiveTab] = useState('login');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const [forgotEmail, setForgotEmail] = useState('');
  const [otpStep, setOtpStep] = useState(1);
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [otpCodeInput, setOtpCodeInput] = useState('');
  const [otpNewPassword, setOtpNewPassword] = useState('');
  const [showOtpModal, setShowOtpModal] = useState(false);

  const API_BASE = window.location.origin + "/api/v1/auth";

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', loginEmail);
    formData.append('password', loginPassword);

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        showToast("Connexion réussie ! Bienvenue sur PlatformActia.");
        onLoginSuccess(data.access_token);
      } else {
        showToast(data.detail || "Email ou mot de passe incorrect", 'error');
      }
    } catch (err) {
      showToast("Erreur de connexion au serveur", 'error');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: regFullName, email: regEmail, password: regPassword })
      });
      const data = await res.json();
      if (res.ok) {
        showToast("Compte Responsable créé avec succès ! Connectez-vous.");
        setRegFullName(''); setRegEmail(''); setRegPassword('');
        setActiveTab('login');
      } else {
        showToast(data.detail || "Erreur d'inscription", 'error');
      }
    } catch (err) {
      showToast("Erreur de connexion au serveur", 'error');
    }
  };

  const handleSendOTP = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail })
      });
      const data = await res.json();
      if (res.ok && data.otp_code) {
        setGeneratedOtp(data.otp_code);
        setShowOtpModal(true);
      } else {
        showToast(data.detail || "Aucun compte associé à cet email", 'error');
      }
    } catch (err) {
      showToast("Erreur lors de l'envoi de l'OTP", 'error');
    }
  };

  const handleResetWithOTP = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail, otp_code: otpCodeInput, new_password: otpNewPassword })
      });
      const data = await res.json();
      if (res.ok) {
        showToast("Mot de passe réinitialisé ! Vous pouvez vous connecter.");
        setOtpStep(1); setForgotEmail(''); setOtpCodeInput(''); setOtpNewPassword('');
        setActiveTab('login');
      } else {
        showToast(data.detail || "Code OTP invalide", 'error');
      }
    } catch (err) {
      showToast("Erreur de réinitialisation", 'error');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'var(--color-primary)', color: '#00141a', fontWeight: '800', fontSize: '2rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '10px' }}>P</div>
        <h1 style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>PlatformActia</h1>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Portail Sécurisé Responsable HSE · CIPI ACTIA</p>
      </div>

      <div className="glass-card" style={{ width: '100%', maxWidth: '440px' }}>
        <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid rgba(0,201,150,0.2)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
          <button onClick={() => setActiveTab('login')} style={{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'login' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'login' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}><LogIn size={16}/> Connexion</button>
          <button onClick={() => setActiveTab('register')} style={{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'register' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'register' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}><UserPlus size={16}/> Inscription</button>
          <button onClick={() => setActiveTab('forgot')} style={{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'forgot' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'forgot' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}><ShieldAlert size={16}/> Oublié</button>
        </div>

        {activeTab === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">Email Responsable</label>
              <input type="email" className="form-input" placeholder="ex: responsable@actia.com" value={loginEmail} onChange={e => setLoginEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Mot de passe</label>
              <input type="password" className="form-input" placeholder="Votre mot de passe" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}><LogIn size={18}/> Se Connecter</button>
          </form>
        )}

        {activeTab === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="form-label">Nom complet</label>
              <input type="text" className="form-input" placeholder="ex: Jean Dupont" value={regFullName} onChange={e => setRegFullName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Adresse Email</label>
              <input type="email" className="form-input" placeholder="ex: responsable@actia.com" value={regEmail} onChange={e => setRegEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Mot de passe (Min 8 caractères)</label>
              <input type="password" className="form-input" placeholder="Choisissez un mot de passe" minLength={8} value={regPassword} onChange={e => setRegPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}><UserPlus size={18}/> Créer le compte</button>
          </form>
        )}

        {activeTab === 'forgot' && otpStep === 1 && (
          <form onSubmit={handleSendOTP}>
            <div className="form-group">
              <label className="form-label">Adresse Email enregistrée</label>
              <input type="email" className="form-input" placeholder="ex: responsable@actia.com" value={forgotEmail} onChange={e => setForgotEmail(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}><Send size={18}/> Obtenir le code OTP</button>
          </form>
        )}

        {activeTab === 'forgot' && otpStep === 2 && (
          <form onSubmit={handleResetWithOTP}>
            <div className="form-group">
              <label className="form-label">Code OTP à 6 chiffres</label>
              <input type="text" className="form-input" placeholder="ex: 123456" maxLength={6} value={otpCodeInput} onChange={e => setOtpCodeInput(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Nouveau mot de passe</label>
              <input type="password" className="form-input" placeholder="Min 8 caractères" minLength={8} value={otpNewPassword} onChange={e => setOtpNewPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}><CheckCircle2 size={18}/> Réinitialiser le mot de passe</button>
            <button type="button" className="btn btn-secondary" style={{ width: '100%', marginTop: '10px' }} onClick={() => setOtpStep(1)}><ArrowLeft size={16}/> Recommencer</button>
          </form>
        )}
      </div>

      {showOtpModal && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff' }}>Code OTP de Sécurité</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '10px 0' }}>Voici votre code temporaire pour la réinitialisation :</p>
            <div style={{ background: 'rgba(0,201,150,0.15)', border: '2px dashed var(--color-primary)', borderRadius: '12px', padding: '1rem', fontSize: '1.8rem', fontWeight: '800', color: 'var(--color-primary)', letterSpacing: '4px', margin: '1rem 0' }}>
              {generatedOtp}
            </div>
            <button className="btn btn-primary" onClick={() => { setOtpCodeInput(generatedOtp); setShowOtpModal(false); setOtpStep(2); }}>Continuer</button>
          </div>
        </div>
      )}
    </div>
  );
}
