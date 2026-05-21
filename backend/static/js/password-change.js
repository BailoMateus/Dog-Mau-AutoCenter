/**
 * password-change.js
 * Gerencia alteração de senha do usuário
 */

document.addEventListener('DOMContentLoaded', () => {
  const changePasswordBtn = document.getElementById('changePasswordBtn');
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', handlePasswordChange);
  }

  // Toggle de visibilidade de senha
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      const isPassword = input.type === 'password';
      
      input.type = isPassword ? 'text' : 'password';
      btn.innerHTML = isPassword ? 
        '<i class="bi bi-eye-slash"></i>' : 
        '<i class="bi bi-eye"></i>';
    });
  });
});

async function handlePasswordChange() {
  const senhaAtual = document.getElementById('senhaAtual').value;
  const novaSenha = document.getElementById('novaSenha').value;
  const confirmarSenha = document.getElementById('confirmarSenha').value;

  // Validações no frontend
  if (!senhaAtual || !novaSenha || !confirmarSenha) {
    UINotification.toast('Preencha todos os campos', 'warning');
    return;
  }

  if (novaSenha.length < 6) {
    UINotification.toast('Nova senha deve ter no mínimo 6 caracteres', 'warning');
    return;
  }

  if (novaSenha !== confirmarSenha) {
    UINotification.toast('As novas senhas não coincidem', 'error');
    return;
  }

  if (senhaAtual === novaSenha) {
    UINotification.toast('Nova senha deve ser diferente da atual', 'warning');
    return;
  }

  // Confirmação
  const confirmado = await UINotification.confirm(
    'Alterar Senha',
    'Tem certeza que deseja alterar sua senha? Você precisará fazer login novamente.',
    'Alterar'
  );

  if (!confirmado) return;

  // Loading
  const loading = UINotification.loading('Alterando senha...');
  loading.show();

  try {
    const response = await fetch('/api/me/password-change', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        old_password: senhaAtual,
        new_password: novaSenha,
        confirm_password: confirmarSenha
      })
    });

    loading.hide();

    if (!response.ok) {
      const error = await response.json();
      console.error('Erro ao alterar senha:', error);
      UINotification.toast(
        error.detail || 'Erro ao alterar senha',
        'error'
      );
      return;
    }

    UINotification.toast('Senha alterada com sucesso! Redirecionando...', 'success');

    // Limpar formulário
    document.getElementById('senhaAtual').value = '';
    document.getElementById('novaSenha').value = '';
    document.getElementById('confirmarSenha').value = '';

    // Redirecionar após 2s (força relogin)
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);

  } catch (error) {
    loading.hide();
    console.error('Erro:', error);
    UINotification.toast('Erro ao alterar senha. Tente novamente.', 'error');
  }
}

window.handlePasswordChange = handlePasswordChange;