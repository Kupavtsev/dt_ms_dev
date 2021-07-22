'use strict'

console.log('Connected to Script')

const mainFrom = document.querySelector('#request-form');

const loginInput = document.querySelector('#form_login');
const passwordInput = document.querySelector('#form_password');
const emailServiceInput = document.querySelector('#form_email');
const keyWordsInput = document.querySelector('#form_keywords');
const resultTextArea = document.querySelector('#form_result');

let btnCheckMail = document.getElementsByClassName('btn btn-success btn-send')[0];
let btnShowResult = document.getElementsByClassName('btn btn-send')[1];

// btnCheckMail.addEventListener('click', function (e) {
//     console.log(this.btnCheckMail)
// })


// ======   BLL   ======

let mail_service, login, password, keyWords;

mainFrom.addEventListener('submit', onSubmit)

function onSubmit(e) {
    e.preventDefault();
    btnCheckMail.setAttribute('disabled', 'disabled')

    mail_service = 'imap.yandex.ru'
    login = loginInput.value
    password = passwordInput.value
    keyWords = keyWordsInput.value

    let request = {
        mail_service,
        login,
        password,
        keyWords
    }

    // console.log(request)


    fetch('http://127.0.0.1:5000/account', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mail_service,
            login,
            password,
            keyWords
        })
    }
    )
    .then((response) => {
        // console.log(response)
        btnShowResult.removeAttribute('disabled')
        btnCheckMail.removeAttribute('disabled')
    })
}

// Check data from DB
btnShowResult.addEventListener('click', function (e) {
    e.preventDefault();
    getDataWithFetch();
    // console.log('CheckData')
})


// Getting DATA from DB
let getDataWithFetch = () => {
    let login = loginInput.value;
    if (login.length < 1) {
        alert('Введите Login имэйла');
    }
    // fetch('http://127.0.0.1:5000/senders')
    fetch('http://127.0.0.1:5000/senders?login=' + login)
        .then((response) => {
            // console.log(typeof login)
            // console.log(login)
            // console.log(fetch('http://127.0.0.1:5000/senders?login=' + {login}))
            return response.json();
        })
      
        .then((data) => {
            // console.log(typeof data)
            // console.log(data.length)
            let count_data = data.length
            if (count_data = 1) {
                // console.log(data[0]['Send Date'])
                let date_str = data[0]['Send Date'].substring(0, 16)
            } else {
                // console.log(data[3]['Send Date'])
                let date_str = data[3]['Send Date'].substring(0, 16)
            }
            
           
            if (data.length > 0) {
                let temp = '';
                let id = data.length
                data.forEach((itemData) => {
                    if (loginInput.value == itemData['Recipient']) {
                        temp += "<tr>";
                        temp += "<td>" + id + "</td>"
                        temp += "<td>" + itemData['Send Date'].substring(0, 16) + "</td>"
                        temp += "<td>" + itemData['sender'] + "</td>"
                        temp += "<td>" + itemData['Subscription'] + "</td></tr>";
                        --id;
                    }
                });
                document.getElementById('data').innerHTML = temp;
            }

        })
}


