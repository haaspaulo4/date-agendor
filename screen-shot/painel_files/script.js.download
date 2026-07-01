document.addEventListener('DOMContentLoaded', () => {
    // 1. Efeito de Evasão do Botão NÃO
    const btnNo = document.getElementById('btn-no');

    if (btnNo) {
        const moveButton = () => {
            btnNo.classList.add('evade');

            const btnWidth = btnNo.offsetWidth || 100;
            const btnHeight = btnNo.offsetHeight || 50;

            const maxX = window.innerWidth - btnWidth - 30;
            const maxY = window.innerHeight - btnHeight - 30;

            const randomX = Math.max(15, Math.floor(Math.random() * maxX));
            const randomY = Math.max(15, Math.floor(Math.random() * maxY));

            btnNo.style.left = `${randomX}px`;
            btnNo.style.top = `${randomY}px`;
        };

        btnNo.addEventListener('mouseover', moveButton);
        btnNo.addEventListener('mouseenter', moveButton);

        btnNo.addEventListener('touchstart', (e) => {
            e.preventDefault();
            moveButton();
        });

        btnNo.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Erro de sistema: Opção indisponível temporariamente. Por favor, clique em SIM!');
            moveButton();
        });
    }

    // 2. Engine de Partículas de Coração por Trás (Apenas Unicode símbolos, sem Emojis)
    const heartContainer = document.getElementById('heart-container');
    if (heartContainer) {
        const heartShapes = ['♥', '♡'];

        setInterval(() => {
            const heart = document.createElement('div');
            heart.classList.add('floating-heart');

            // Escolhe símbolo randômico
            heart.innerText = heartShapes[Math.floor(Math.random() * heartShapes.length)];

            // Posição x inicial aleatória
            heart.style.left = `${Math.random() * 100}vw`;

            // Tamanho flutuante aleatório
            const size = Math.random() * 18 + 10; // 10px a 28px
            heart.style.fontSize = `${size}px`;

            // Duração da animação flutuante aleatória (3 a 6 segundos)
            const duration = Math.random() * 3 + 3;
            heart.style.animationDuration = `${duration}s`;

            // Opacidade aleatória
            heart.style.opacity = Math.random() * 0.4 + 0.3;

            heartContainer.appendChild(heart);

            // Limpa o nó após conclusão da animação
            setTimeout(() => {
                heart.remove();
            }, duration * 1000);
        }, 350); // Spawna a cada 350ms
    }
});
