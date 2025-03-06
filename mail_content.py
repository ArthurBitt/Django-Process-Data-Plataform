def conteudo_email(email, raw_password):
    conteudo = f'''
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins" rel="stylesheet">

        <title>Email Robo</title>

    </head>

    <body style="font-family: Arial, Helvetica, sans-serif">
        <div class="container" style="background-color: #2c8683; height: 330px; border-radius: 26px;">
            <center>
                <div>
                    <img style="margin-top: 25px;" height="120" src="https://user-images.githubusercontent.com/44476076/161403198-ae58c779-ffac-40a4-a99b-6d4968c143c2.png" alt="">
                </div>
                <div style="margin-top: 20px; color: white;">
                    <h2>Seja bem vindo!</h2>
                </div>
                <h3 style="color: white;">Seu Email de acesso é: {email}</h3>
                <h3 style="color: white;">
                    Sua Senha de acesso é: {raw_password}
                </h3>
                <h3 style="color: white;">
                    Link para login: 
                    <a href="https://gp.squadytecnologia.com.br/accounts/login/">
                        Clique aqui
                    </a>
                </h3>
            </center>
        </div>
    </body>

    </html>'''

    return conteudo
