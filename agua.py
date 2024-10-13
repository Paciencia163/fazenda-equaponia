# Imports necessários
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Nome do arquivo onde os dados serão salvos
DATA_FILE = 'dados_aquaponia.csv'

# Função para carregar os dados armazenados
def carregar_dados():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['pH', 'Temperatura', 'Amônia', 'Nitrito', 'Nitrato', 'Oxigênio', 'Data'])

# Função para salvar novos dados
def salvar_dados(novos_dados):
    df = carregar_dados()
    df = pd.concat([df, novos_dados], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Função para enviar alertas por email
def enviar_email_alerta(alertas):
    remetente = 'pacienciaanibalmuienga@gmail.com'
    destinatario = 'paciencia163@gmail.com'
    senha = 'pescadores'

    # Configurar a mensagem do email
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = 'Alerta de Qualidade da Água - Aquaponia'
    
    # Conteúdo do email
    corpo = '\n'.join(alertas)
    msg.attach(MIMEText(corpo, 'plain'))

    # Configurar o servidor SMTP e enviar o email
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remetente, senha)
        texto = msg.as_string()
        servidor.sendmail(remetente, destinatario, texto)
        servidor.quit()
        st.success("Alerta de email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar email: {str(e)}")

# Função para avaliar os parâmetros da água e gerar alertas visuais
def avaliar_agua(pH, temperatura, amonia, nitrito, nitrato, oxigenio_dissolvido):
    resultados = []
    alertas = []
    
    # Avaliação de pH
    if pH < 6.0 or pH > 7.5:
        resultados.append('O pH está fora da faixa ideal (6.0-7.5).')
        alertas.append('pH fora da faixa! Verifique o sistema.')
        st.error('⚠️ Atenção: pH fora da faixa ideal!')
    else:
        st.success('✅ pH dentro da faixa ideal.')

    # Avaliação de temperatura
    if temperatura < 18 or temperatura > 30:
        resultados.append('A temperatura da água está fora da faixa ideal (18-30°C).')
        alertas.append('Temperatura fora da faixa! Verifique o sistema.')
        st.error('⚠️ Atenção: Temperatura fora da faixa ideal!')
    else:
        st.success('✅ Temperatura dentro da faixa ideal.')

    # Avaliação de amônia
    if amonia > 0.5:
        resultados.append('Os níveis de amônia estão altos! Pode ser tóxico para os peixes.')
        alertas.append('Amônia alta! Pode ser perigoso.')
        st.error('⚠️ Atenção: Amônia acima do limite recomendado!')
    else:
        st.success('✅ Amônia dentro da faixa segura.')

    # Avaliação de nitrito
    if nitrito > 0.5:
        resultados.append('Os níveis de nitrito estão acima do limite recomendado (máx 0.5 ppm).')
        alertas.append('Nitrito acima do limite! Verifique o sistema.')
        st.error('⚠️ Atenção: Nitrito acima do limite recomendado!')
    else:
        st.success('✅ Nitrito dentro do limite seguro.')

    # Avaliação de nitrato
    if nitrato > 40:
        resultados.append('Os níveis de nitrato estão altos (máx 40 ppm).')
        alertas.append('Nitrato alto! Verifique o sistema.')
        st.error('⚠️ Atenção: Nitrato acima do limite recomendado!')
    else:
        st.success('✅ Nitrato dentro do limite seguro.')

    # Avaliação de oxigênio dissolvido
    if oxigenio_dissolvido < 4.0:
        resultados.append('Níveis baixos de oxigênio dissolvido! Aumente a aeração da água.')
        alertas.append('Oxigênio baixo! Aumente a aeração.')
        st.error('⚠️ Atenção: Níveis baixos de oxigênio dissolvido!')
    else:
        st.success('✅ Níveis adequados de oxigênio dissolvido.')

    if not resultados:
        return "Todos os parâmetros estão dentro da faixa ideal!", alertas
    return '\n'.join(resultados), alertas

# Título do Aplicativo
st.title('Monitoramento de Qualidade da Água - Fazenda de Aquaponia Sustentável')

# Entrada de Parâmetros
st.header("Insira os parâmetros da qualidade da água:")
pH = st.slider('pH da água', 0.0, 14.0, 7.0)
temperatura = st.slider('Temperatura da água (°C)', 0, 40, 25)
amonia = st.number_input('Nível de Amônia (NH3) - ppm', min_value=0.0, max_value=10.0, value=0.5)
nitrito = st.number_input('Nível de Nitrito (NO2) - ppm', min_value=0.0, max_value=10.0, value=0.5)
nitrato = st.number_input('Nível de Nitrato (NO3) - ppm', min_value=0.0, max_value=100.0, value=10.0)
oxigenio_dissolvido = st.slider('Oxigênio Dissolvido (mg/L)', 0.0, 10.0, 5.0)

# Botão para processar dados
if st.button('Avaliar Qualidade da Água'):
    # Avaliar os dados e gerar alertas
    avaliacao, alertas = avaliar_agua(pH, temperatura, amonia, nitrito, nitrato, oxigenio_dissolvido)
    st.subheader('Avaliação dos Parâmetros:')
    st.write(avaliacao)

    # Capturar a data atual
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Criar DataFrame com os novos dados
    novos_dados = pd.DataFrame({
        'pH': [pH],
        'Temperatura': [temperatura],
        'Amônia': [amonia],
        'Nitrito': [nitrito],
        'Nitrato': [nitrato],
        'Oxigênio': [oxigenio_dissolvido],
        'Data': [data_atual]
    })

    # Salvar os novos dados
    salvar_dados(novos_dados)
    st.success("Dados salvos com sucesso!")

    # Enviar email se houver alertas
    if alertas:
        enviar_email_alerta(alertas)

# Carregar e mostrar os dados armazenados
st.header('Histórico de Qualidade da Água:')
df_dados = carregar_dados()

# Mostrar tabela de dados
st.dataframe(df_dados)

# Gráfico dos parâmetros ao longo do tempo (exemplo com pH e temperatura)
st.subheader('Gráfico dos Parâmetros ao Longo do Tempo')
if not df_dados.empty:
    fig, ax = plt.subplots()
    ax.plot(df_dados['Data'], df_dados['pH'], label='pH', marker='o')
    ax.plot(df_dados['Data'], df_dados['Temperatura'], label='Temperatura', marker='s')
    ax.set_xlabel('Data')
    ax.set_ylabel('Valores')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("Nenhum dado disponível para exibir.")
