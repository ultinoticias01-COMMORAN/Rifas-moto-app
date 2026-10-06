import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Rifa Digital", page_icon="🎟️️", layout="centered")

DB_FILE = "base_datos_rifa.csv"

# 1. Inicializar la base de datos si no existe (10,000 números del 0000 al 9999)
@st.cache_data
def cargar_o_crear_bd():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'Numero': str})
    else:
        numeros = [f"{i:04d}" for i in range(10000)]
        df = pd.DataFrame({
            "Numero": numeros,
            "Estado": "Disponible", 
            "Comprador": "",
            "Cedula": "",
            "Telefono": "",
            "Referencia": ""
        })
        df.to_csv(DB_FILE, index=False)
        return df

df_rifa = cargar_o_crear_bd()

# Título Principal
st.title("🎟️ Gran Rifa: Moto 250cc + Premios en Efectivo")
st.markdown("### ¡Participa y gana! 🚀")

# Menú lateral para cambiar entre comprar, consultar o administrar
menu = st.sidebar.selectbox("Menú", ["Comprar Boletos", "Consultar mis Números", "Administración"])

if menu == "Comprar Boletos":
    # Mostrar estadísticas rápidas de disponibilidad
    total_vendidos = len(df_rifa[df_rifa["Estado"] == "Vendido"])
    total_disponibles = len(df_rifa[df_rifa["Estado"] == "Disponible"])
    
    col1, col2 = st.columns(2)
    col1.metric("Boletos Disponibles", total_disponibles)
    col2.metric("Boletos Vendidos 🎟️", total_vendidos)
    
    st.divider()

    # Formulario de compra con asignación al azar
    with st.form("form_compra_azar"):
        st.subheader("📝 Tus Datos Personales")
        nombre = st.text_input("Nombre y Apellido")
        cedula = st.text_input("Cédula de Identidad")
        telefono = st.text_input("Teléfono (WhatsApp)")
        
        st.subheader("🔢 Cantidad de Boletos")
        cantidad = st.number_input("¿Cuántos números deseas comprar?", min_value=1, max_value=20, value=1, step=1)
        st.caption("💡 El sistema te asignará números al azar automáticamente al confirmar.")
        
        st.subheader("💳 Datos de Pago Móvil")
        st.info("Realiza tu pago y coloca los últimos 4 dígitos de la referencia bancaria.")
        referencia = st.text_input("Últimos 4 dígitos de la Referencia")
        
        enviar = st.form_submit_button("¡Comprar y Obtener Mis Números! 🚀")
        
        if enviar:
            if not nombre or not telefono or not referencia or not cedula:
                st.error("⚠️ Por favor completa todos los campos obligatorios.")
            else:
                # Filtrar números disponibles
                disponibles_df = df_rifa[df_rifa['Estado'] == 'Disponible']
                
                if len(disponibles_df) < cantidad:
                    st.error("❌ Lo sentimos, no hay suficientes números disponibles para esa cantidad.")
                else:
                    # Seleccionar al azar la cantidad exacta solicitada
                    asignados = disponibles_df.sample(n=int(cantidad))['Numero'].tolist()
                    
                    # Actualizar la base de datos
                    for n in asignados:
                        df_rifa.loc[df_rifa['Numero'] == n, 'Estado'] = 'Vendido'
                        df_rifa.loc[df_rifa['Numero'] == n, 'Comprador'] = nombre
                        df_rifa.loc[df_rifa['Numero'] == n, 'Cedula'] = cedula
                        df_rifa.loc[df_rifa['Numero'] == n, 'Telefono'] = telefono
                        df_rifa.loc[df_rifa['Numero'] == n, 'Referencia'] = referencia
                    
                    # Guardar cambios en el archivo CSV
                    df_rifa.to_csv(DB_FILE, index=False)
                    
                    # Mostrar éxito y los números asignados
                    st.success(f"🎉 ¡Felicidades {nombre}! Se te han asignado los siguientes números al azar:")
                    st.markdown(f"### **{', '.join(asignados)}**")
                    st.balloons()
                    st.info("📸 Guarda una captura de pantalla de estos números junto con tu comprobante de pago.")

elif menu == "Consultar mis Números":
    st.header("🔍 Consulta tus Boletos")
    st.markdown("Ingresa tu número de teléfono registrado para ver los boletos que el sistema te asignó.")
    
    tel_consulta = st.text_input("Número de Teléfono (ej: 0414...)")
    if tel_consulta:
        comprados = df_rifa[df_rifa['Telefono'].str.contains(tel_consulta, na=False)]
        if not comprados.empty:
            nombre_cliente = comprados.iloc[0]['Comprador']
            st.success(f"✅ ¡Hola, {nombre_cliente}! Aquí tienes tus números registrados:")
            st.dataframe(comprados[['Numero', 'Estado', 'Referencia']], use_container_width=True)
        else:
            st.warning("⚠️ No se encontraron boletos asociados a ese número de teléfono.")

elif menu == "Administración":
    st.header("⚙️ Panel de Control")
    password = st.text_input("Contraseña de Administrador", type="password")
    
    if password == "admin123":
        st.success("Acceso concedido 🔓")
        
        filtro = st.selectbox("Ver registros", ["Todos", "Vendidos", "Disponibles"])
        if filtro == "Vendidos":
            df_ver = df_rifa[df_rifa['Estado'] == 'Vendido']
        elif filtro == "Disponibles":
            df_ver = df_rifa[df_rifa['Estado'] == 'Disponible']
        else:
            df_ver = df_rifa
            
        st.dataframe(df_ver, use_container_width=True)
        
        st.download_button(
            label="📥 Descargar Base de Datos (CSV)",
            data=df_rifa.to_csv(index=False).encode('utf-8'),
            file_name="respaldo_rifa.csv",
            mime="text/csv"
        )
    elif password != "":
        st.error("❌ Contraseña incorrecta")
