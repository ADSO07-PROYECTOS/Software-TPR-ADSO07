document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('registroForm').addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Registro exitoso. Los datos han sido enviados correctamente.');
    });
});
