/**
 * auth-interceptor.js
 * 
 * Intercepta requisições de API e redireciona para /cadastro quando retorna 401 (não autenticado).
 * Útil para garantir que usuários não autenticados que tentam fazer compras sejam redirecionados.
 */

// Armazena o fetch original
const originalFetch = window.fetch;

// Substitui o fetch global com versão interceptadora
window.fetch = function(...args) {
    return originalFetch.apply(this, args)
        .then(async (response) => {
            // Se receber 401 Unauthorized
            if (response.status === 401) {
                console.warn("[Auth Interceptor] Acesso negado (401) — redirecionando para cadastro");
                // Redireciona para a página de cadastro
                window.location.href = '/cadastro';
                // Retorna uma promise que nunca resolve (para evitar processamento)
                return new Promise(() => {});
            }
            return response;
        })
        .catch((error) => {
            console.error("[Auth Interceptor] Erro ao fazer requisição:", error);
            throw error;
        });
};
