import {header,userDeslogado,userLogado} from './componentes-js/header.js'
import {carrossel} from'./componentes-js/carrossel.js'
import {footer} from './componentes-js/footer.js'

// Script geral pra ter as integrações entre o front e o back
let logado = true;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("header").innerHTML = header;

    if (logado) {
        document.getElementById("user-area").innerHTML = userLogado;
    } else {
        document.getElementById("user-area").innerHTML = userDeslogado;
    }

    document.getElementById("carrossel").innerHTML = carrossel;
    document.getElementById("footer").innerHTML = footer;

    document.getElementById("carrosselItem1").src = "assets/navbar.png"
    document.getElementById("carrosselItem2").src = "assets/navbar.png"
    document.getElementById("carrosselItem3").src = "assets/navbar.png"
})
