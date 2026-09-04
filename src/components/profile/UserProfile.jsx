import React, { useState } from 'react';
import { User, Mail, Shield, Lock, Save } from 'lucide-react';

export default function UserProfile({ user, showToast }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const handleChangePassword = async (e) => {
    e.preventDefault();
    const API_BASE = window.location.origin + "/api/v1/auth";
    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(`${API_BASE}/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
      });
      const data = await res.json();
      if (res.ok) {
        showToast("Mot de passe mis à jour avec succès !");
        setOldPassword(''); setNewPassword('');
      } else {
        showToast(data.detail || "Ancien mot de passe incorrect", 'error');
      }
    } catch (err) {
      showToast("Erreur lors de la mise à jour", 'error');
    }
  };

  const initial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'R';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
      
      {/* PROFILE CARD */}
      <div className="glass-card">
        <div style={{ textAlign: 'center', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid rgba(0,201,150,0.2)' }}>
          <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--color-primary)', color: '#00141a', fontWeight: '800', fontSize: '2.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
            {initial}
          </div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#fff' }}>{user?.full_name || 'Responsable HSE'}</h2>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-primary)', fontWeight: '700', marginTop: '2px' }}>Responsable HSE · CIPI ACTIA</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: '700' }}>Identifiant Responsable</span>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff', marginTop: '2px' }}>#ACTIA-{user?.id || '1'}</div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: '700' }}>Adresse Email</span>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff', marginTop: '2px' }}>{user?.email || 'responsable@actia.com'}</div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: '700' }}>Site / Organisation</span>
            <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff', marginTop: '2px' }}>CIPI ACTIA</div>
          </div>
        </div>
      </div>

      {/* SECURITY CARD */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Shield size={20} color="var(--color-primary)" /> Sécurité du Compte
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Modifiez votre mot de passe pour sécuriser l'accès à vos données HSE.
        </p>

        <form onSubmit={handleChangePassword}>
          <div className="form-group">
            <label className="form-label">Ancien mot de passe</label>
            <input type="password" className="form-input" placeholder="Mot de passe actuel" value={oldPassword} onChange={e => setOldPassword(e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Nouveau mot de passe (Min 8 caractères)</label>
            <input type="password" className="form-input" placeholder="Minimum 8 caractères" minLength={8} value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
            <Save size={18} /> Mettre à jour le mot de passe
          </button>
        </form>
      </div>

    </div>
  );
}
