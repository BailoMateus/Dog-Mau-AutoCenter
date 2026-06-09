/**
 * session-timeout.js
 *
 * Desloga o usuário automaticamente após 1 hora sem qualquer atividade no sistema.
 * Só atua quando há um usuário autenticado (meta current-user-id preenchida).
 */
(function () {
    const userMeta = document.querySelector('meta[name="current-user-id"]');
    const currentUserId = userMeta ? userMeta.content : '';

    // Sem usuário logado não há sessão para expirar.
    if (!currentUserId) return;

    const INACTIVITY_LIMIT_MS = 60 * 60 * 1000; // 1 hora
    let inactivityTimer = null;

    function logout() {
        window.location.href = '/logout';
    }

    function resetTimer() {
        if (inactivityTimer) clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(logout, INACTIVITY_LIMIT_MS);
    }

    const activityEvents = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    activityEvents.forEach((evt) => {
        window.addEventListener(evt, resetTimer, { passive: true });
    });

    resetTimer();
})();
