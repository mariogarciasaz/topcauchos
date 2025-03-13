document.addEventListener('DOMContentLoaded', function () {
    console.log("main.js cargado correctamente");

    /* ==============================
       FUNCIONALIDAD PARA AGREGAR CARROS
       ============================== */

    function openPopup() {
        document.getElementById("popupForm").style.display = "block";
    }

    function closeAddPopup() {
        document.getElementById("popupForm").style.display = "none";
    }

    function submitAddForm(event) {
        event.preventDefault();  // Prevenir el envío normal del formulario

        var form = event.target;
        var formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Carro agregado exitosamente");
                closeAddPopup();
                location.reload();  // Recargar la página para reflejar cambios
            } else {
                alert("Hubo un error al agregar el carro");
                console.log(data.errors);
            }
        })
        .catch(error => {
            alert("Ocurrió un error al procesar la solicitud.");
            console.log(error);
        });
    }

    let addCarForm = document.querySelector("#popupForm form");
    if (addCarForm) {
        addCarForm.addEventListener("submit", submitAddForm);
    }

    /* ==============================
       FUNCIONALIDAD PARA EDITAR CARROS
       ============================== */

    function openEditPopup(carId) {
        console.log("Abriendo popup de edición para el carro con ID:", carId);

        document.getElementById("editPopupForm").style.display = "block";

        // Obtener los datos del carro
        fetch(`/edit_car/11/`)  // Asegúrate de que esta URL sea la correcta
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("car_id").value = data.car.id;
                    document.getElementById("carBrand").value = data.car.brand;
                    document.getElementById("carModel").value = data.car.model;
                    document.getElementById("carYear").value = data.car.year;
                    document.getElementById("carColor").value = data.car.color;
                    document.getElementById("carLicensePlate").value = data.car.license_plate;
                    document.getElementById("carKms").value = data.car.kms;
                    document.getElementById("carLastService").value = data.car.last_service_date || '';
                } else {
                    alert("No se pudo cargar el carro. Intenta nuevamente.");
                }
            })
            .catch(error => {
                console.error('Error al obtener los datos:', error);
                alert('Hubo un error al cargar los datos del carro.');
            });
    }

    function closeEditPopup() {
        document.getElementById("editPopupForm").style.display = "none";
    }

    let editCarForm = document.getElementById("editCarForm");
    if (editCarForm) {
        editCarForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const carId = formData.get('car_id');

            fetch(`/edit_car/${carId}/`, {  
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Carro actualizado correctamente');
                    closeEditPopup();
                    location.reload();
                } else {
                    alert('Hubo un error al actualizar el carro');
                    console.log(data.errors);
                }
            })
            .catch(error => {
                console.error('Error al enviar el formulario:', error);
                alert('Hubo un error al actualizar el carro.');
            });
        });
    }

    /* ==============================
       EVENTOS PARA ABRIR/CERRAR POPUPS
       ============================== */

    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", function () {
            const carId = button.getAttribute("data-car-id");
            openEditPopup(carId);
        });
    });

    window.onclick = function (event) {
        let editPopup = document.getElementById("editPopupForm");
        let addPopup = document.getElementById("popupForm");
        if (event.target === editPopup) {
            closeEditPopup();
        } else if (event.target === addPopup) {
            closeAddPopup();
        }
    };
});
