function updateUsers() {
    var select = document.getElementById("UserSelect");
    var userId = select.value;

    fetch(`/get-user-info/${userId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("UserName").value = data.nombre_usuario;
            document.getElementById("UserPassword").value = ""; 
        })
        .catch(error => console.error('Error:', error));
}

function updateAccount() {
    var select = document.getElementById("accountSelect");
    var AccountId = select.value;

    fetch(`/get-account-info/${AccountId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("newAccountName").value = data.nombre_cuenta;
            document.getElementById("newAccountID").value = data.cuenta_id; 
        })
        .catch(error => console.error('Error:', error));
}

function updateScriptE() {
    var select = document.getElementById("scriptESelect");
    var AccountId = select.value;

    fetch(`/get-account-E/${AccountId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("preview").textContent = data.descripcion;
        })
        .catch(error => console.error('Error:', error));
}

function duplicateFields() {
    const number = document.getElementById('fieldSelect').value;
    const container = document.getElementById('dynamicFieldsContainer');
    container.innerHTML = ''; 

    for (let i = 1; i <= number; i++) {
        const fieldSet = document.createElement('div');
        fieldSet.className = 'row justify-content-center mb-3'; 
        fieldSet.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">Correo #${i}</label>
                    <input type="text" class="form-control" id="correo[]" name="correo[]" placeholder="Ingrese correo">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Extensión #${i}</label>
                    <input type="text" class="form-control" id="extension[]" name="extension[]" placeholder="Ingrese extensión">
                </div>
            </div>
        `;
        container.appendChild(fieldSet);
    }
}

function duplicateFieldsB() {
    const number = document.getElementById('fieldSelectB').value;
    const container = document.getElementById('dynamicFieldsContainerB');
    container.innerHTML = ''; 

    for (let i = 1; i <= number; i++) {
        const fieldSet = document.createElement('div');
        fieldSet.className = 'row justify-content-center mb-3'; 
        fieldSet.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">Correo Baja #${i}</label>
                    <input type="text" class="form-control" id="correoB[]" name="correoB[]" placeholder="Ingrese correo">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Extensión Baja #${i}</label>
                    <input type="text" class="form-control" id="extensionB[]" name="extensionB[]" placeholder="Ingrese extensión">
                </div>
            </div>
        `;
        container.appendChild(fieldSet);
    }
}


/* Modal Cuentas */
function openModalDeleteAccount(accountID) {
    var modal = new bootstrap.Modal(document.getElementById('deleteAccountModal'));
    modal.show();

    document.getElementById('confirmDelete').onclick = function() {
        var form = document.createElement('form');
        form.action = `/delete-account/${accountID}`;
        form.method = 'post';
        document.body.appendChild(form);
        form.submit();
    };
}

/* Modal Politicas */
function openModalDeletePolicy(policyID) {
    var modal = new bootstrap.Modal(document.getElementById('deletePolicyModal'));
    modal.show();

    document.getElementById('confirmDelete').onclick = function() {
        var form = document.createElement('form');
        form.action = `/delete-policy/${policyID}`;
        form.method = 'post';
        document.body.appendChild(form);
        form.submit();
    };
}

function openModalDeletePolicyB(policyID) {
    var modal = new bootstrap.Modal(document.getElementById('deletePolicyModal'));
    modal.show();

    document.getElementById('confirmDelete').onclick = function() {
        var form = document.createElement('form');
        form.action = `/delete-policy-baja/${policyID}`;
        form.method = 'post';
        document.body.appendChild(form);
        form.submit();
    };
}

function openModalDeletePolicyAccount(policyID, accountId) {
    var modal = new bootstrap.Modal(document.getElementById('deletePolicyModal'));
    modal.show();

    document.getElementById('confirmDelete').onclick = function() {
        console.log(policyID)
        console.log(accountId)
        var form = document.createElement('form');
        form.action = `/delete-policy-account/${policyID}/${accountId}`;
        form.method = 'post';
        document.body.appendChild(form);
        form.submit();
    };
}

/* Modal Usuarios*/
function openModalDeleteUser(userId) {
    var modal = new bootstrap.Modal(document.getElementById('deleteUserModal'));
    modal.show();

    document.getElementById('confirmDelete').onclick = function() {
        var form = document.createElement('form');
        form.action = `/delete-user/${userId}`;
        form.method = 'post';
        document.body.appendChild(form);
        form.submit();
    };
}

function openModalAddUser() {
    var formData = new FormData(document.getElementById('userForm'));
    if(formData.checkValidity()){
        var modal = new bootstrap.Modal(document.getElementById('addUserModal'));
        modal.show();
        document.getElementById('confirmAdd').addEventListener('click', function() {
            // AJAX
            fetch('/add-user', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Algo salió mal al agregar el usuario.');
            })
            .then(data => {
                console.log('Usuario agregado:', data);
                bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
                document.getElementById('userForm').reset();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
}

function openModalEditUser() {
    var formData = new FormData(document.getElementById('updateUserForm'));
    if(formData.checkValidity()){
        var modal = new bootstrap.Modal(document.getElementById('editUserModal'));
        modal.show();
        document.getElementById('confirmEdit').addEventListener('click', function() {
            // AJAX
            fetch('/update-user', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Algo salió mal al modificar el usuario.');
            })
            .then(data => {
                console.log('Usuario modificado:', data);
                bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
                document.getElementById('updateUserForm').reset();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
}
