document.addEventListener('DOMContentLoaded', function(){
const socket = io();

// Evento para manejar el número de usuarios conectados
socket.on('usuarios_conectados', function(numeroUsuarios) {
    console.log('Usuarios conectados: ' + numeroUsuarios);
    document.getElementById('numero-usuarios').textContent = numeroUsuarios;
});

// Evento para manejar la llegada de una nueva canción
socket.on('nueva_cancion', function(data) {
    console.log("Recibiendo evento para cancion",data.cancion);
    const cancionesLista = document.getElementById('canciones');
    let cancionExistente = document.getElementById(data.cancion);
    if (!cancionExistente) {
        const nuevaCancion = document.createElement('li');
        nuevaCancion.id = data.cancion
        //nuevaCancion.textContent = ´${data.cancion} - Me gusta: ${data.votos.me_gusta}´;
       
        nuevaCancion.textContent = `${data.cancion} - Me gusta: ${data.votos.me_gusta}`;


        cancionesLista.appendChild(nuevaCancion);
    }
});



socket.on('mensale_flash',function(data){
    alert(data.mensaje);

})





// Evento para actualizar los votos de una canción
socket.on('actualizar_votos', function(data) {
    const cancionElemento = document.getElementById(data.cancion);
    if (cancionElemento) {
        cancionElemento.innerHTML = '${data.cancion} - Me gusta: ${data.votos.me_gusta} ';
    window.location.href='/home';
    }
});

// Evento para redirigir a los resultados al terminar la votación
socket.on('redirigir_resultados', function() {
    window.location.href = '/resultado';
});

// Función para votar por una canción
function votar(cancion, voto) {
    fetch('/votar/${cancion}', {
        method: 'POST',
        body: new URLSearchParams({
            'voto': voto
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Voto registrado');
    })
    .catch(error => console.error('Error al registrar el voto:', error));
}


function votar(cancion, voto) {
    fetch('/votar_k/${cancion}', {
        method: 'POST',
        body: new URLSearchParams({
            'voto': voto
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Voto registrado');
    })
    .catch(error => console.error('Error al registrar el voto:', error));
}

// Event listeners para las votaciones de las canciones
document.querySelectorAll('.votar').forEach(button => {
    button.addEventListener('click', function() {
        const cancion = button.getAttribute('data-cancion');
        const voto = button.getAttribute('data-voto');
        votar(cancion, voto);
    });
}); 
});