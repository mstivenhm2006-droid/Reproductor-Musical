import os
import random
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import pygame
class Nodo_Song:
    def __init__(self,ruta):
        self.ruta= ruta
        self.titulo=os.path.splitext(os.path.basename(ruta))[0]
        self.anterior = None
        self.siguiente = None
class ListaDobleCircular:
        def __init__(self):
            self.primero=None
            self.actual = None
            self.tamaño= 0
        def esta_vacia(self):
            return self.primero is None
        def agregar(self,ruta):
            nuevo=Nodo_Song(ruta)
            if self.esta_vacia():
                nuevo.siguiente=nuevo
                nuevo.anterior=nuevo
                self.primero=nuevo
                self.actual=nuevo
            else:
                ultimo=self.primero.anterior
                ultimo.siguiente=nuevo
                nuevo.anterior=ultimo
                nuevo.siguiente=self.primero
                self.primero.anterior=nuevo
            self.tamaño+=1
            return nuevo
        def recorrer(self):
            nodos=[]
            if self.esta_vacia():
                return nodos
            nodo=self.primero
            while True:
                nodos.append(nodo)
                nodo=nodo.siguiente
                if nodo == self.primero:
                    break
                return  nodos
        def siguiente(self):
            if self.actual is None:
                self.actual=self.actual.siguiente
            return self.actual
        def anterior(self):
            if self is None:
                self.actual=self.actual.anterior
            return self.actual
        def buscar_por_indice(self,indice):
            nodos=self.recorrer()
            if 0 <= indice < len(nodos):
                return nodos[indice]
            return None
        def seleccionar(self,nodo):
            if nodo in self.recorrer():
                self.actual= nodo
                return True
            return False
        def eliminar(self,nodo):
            if nodo is None or self.esta_vacia:
                return False
            if self.tamaño==1:
                self.primero = None
                self.actual= None
            else:
                nodo.anterior.siguiente=nodo.siguiente
                nodo.siguiente.anterior=nodo.anterior
            if nodo== self.primero:
                self.primero=nodo.siguiente
            if nodo==self.actual:
                self.actual=nodo.siguiente
            nodo.anterior=None
            nodo.siguiente =None
            self.tamaño -= 1
            return True
        # ---------- FUNCIONES NUEVAS DE LA LISTA ----------
        def lista_nodos(self):
            """Devuelve todos los nodos en orden (una sola vuelta completa)."""
            nodos=[]
            if self.esta_vacia():
                return nodos
            nodo=self.primero
            while True:
                nodos.append(nodo)
                nodo=nodo.siguiente
                if nodo is self.primero:
                    break
            return nodos
        def avanzar(self):
            """Mueve 'actual' al nodo siguiente (circular) y lo devuelve."""
            if self.actual is not None:
                self.actual=self.actual.siguiente
            return self.actual
        def retroceder(self):
            """Mueve 'actual' al nodo anterior (circular) y lo devuelve."""
            if self.actual is not None:
                self.actual=self.actual.anterior
            return self.actual
        def buscar_por_titulo(self,texto):
            """Devuelve los nodos cuyo titulo contiene el texto (sin distinguir mayusculas)."""
            texto=texto.lower().strip()
            return [n for n in self.lista_nodos() if texto in n.titulo.lower()]
        def nodo_aleatorio(self):
            """Devuelve un nodo al azar, o None si la lista esta vacia."""
            nodos=self.lista_nodos()
            return random.choice(nodos) if nodos else None
        def quitar(self,nodo):
            """Elimina un nodo de forma segura. Devuelve True si lo elimino."""
            if nodo is None or self.esta_vacia() or nodo not in self.lista_nodos():
                return False
            if self.tamaño==1:
                self.primero=None
                self.actual=None
            else:
                nodo.anterior.siguiente=nodo.siguiente
                nodo.siguiente.anterior=nodo.anterior
                if nodo is self.primero:
                    self.primero=nodo.siguiente
                if nodo is self.actual:
                    self.actual=nodo.siguiente
            nodo.anterior=None
            nodo.siguiente=None
            self.tamaño-=1
            return True
class reproductorMusica:
        def __init__(self,ventana):
            self.ventana=ventana
            self.ventana.title("Reproductor musical")
            self.ventana.geometry("950x620")
            self.ventana.minsize(760,500)
            self.ventana.configure(bg="#101827")
            self.lista= ListaDobleCircular()
            self.pausado =False
            self.volumen=tk.DoubleVar(value=0.65)
            self.mensaje=tk.StringVar(value="Agregar archivos MP3")
            self.camcion_actual=tk.StringVar(value="Ninguna canción seleccionada")

            try:
                pygame.mixer.init()
                self.audio_disponible=True
            except pygame.error as error:
                self.audio_disponible=False
                messagebox.showerror(
                    "Error de audio",
                    "No se puede iniciiar el audio \n"
                    "Compruebe la salida de sonido del PC\n\n"
                    f"Detalle:{error}"
                    )
            self.crear_interfaz()
        def crear_interfaz(self):
            estilo=ttk.Style()
            estilo.theme_use("clam")
            estilo.configure(
                "Treeview",
                background="#17243a",
                foreground="#f1f5f9",
                fieldbackground="#17243a",
                rowheight=30,
                borderwidth=0
            )
            estilo.configure(
                "Treeview.Heading",
                background="#253650",
                foreground="#ffffff",
                font=("Segoe UI",10 ,"bold")
            )
            estilo.map(
                "Treeview",
                background=[("selected","#6554d9")],
                foreground=[("selected", "#ffffff")]
            )
            encabezado= tk.Frame(self.ventana, bg="#101827")
            encabezado.pack(fill="x",padx=24,pady=(20,10))
            tk.Label(
                encabezado,
                text="Reproductor musical",
                font=("segoe UI",21,"bold"),
                fg="#ffffff",
                bg="#101827"
            ).pack(anchor="w")
            tk.Label(
                encabezado,
                text="Lista doblemente enlazada circular",
                font=("Segoe UI", 10),
                fg="#aab8d0",
                bg="#101627"
                ).pack(anchor="w",pady=(4,0))
            contenido =tk.Frame(self.ventana, bg="#101827")
            contenido.pack(fill="both",expand=True,padx=24,pady=8)
            self.construir_controles(contenido)
        # ---------- FUNCIONES NUEVAS DEL REPRODUCTOR ----------
        def iniciar_estado_extra(self):
            """Variables de estado de las funciones nuevas (llamar una vez)."""
            self.reproduciendo=False
            self.aleatorio=tk.BooleanVar(value=False)
            self.repetir=tk.BooleanVar(value=False)
            self.duracion=0.0
            self.desplazamiento=0.0
            self.arrastrando=False
            self.tiempo_texto=tk.StringVar(value="00:00 / 00:00")
            self.busqueda=tk.StringVar()

        def construir_controles(self,contenedor):
            """Crea lista, botones, volumen, progreso y busqueda dentro de 'contenedor'.
            Se llama desde crear_interfaz pasando el frame 'contenido'."""
            self.iniciar_estado_extra()

            # Busqueda
            barra=tk.Frame(contenedor,bg="#101827")
            barra.pack(fill="x",pady=(0,8))
            entrada=tk.Entry(barra,textvariable=self.busqueda)
            entrada.pack(side="left",fill="x",expand=True)
            entrada.bind("<KeyRelease>",lambda e:self.buscar())
            tk.Button(barra,text="Limpiar",command=self.limpiar_busqueda).pack(side="left",padx=(6,0))

            # Lista de canciones
            self.tabla=ttk.Treeview(contenedor,columns=("n","titulo"),show="headings",selectmode="browse")
            self.tabla.heading("n",text="#")
            self.tabla.heading("titulo",text="Titulo")
            self.tabla.column("n",width=50,anchor="center",stretch=False)
            self.tabla.column("titulo",anchor="w")
            self.tabla.pack(fill="both",expand=True)
            self.tabla.bind("<Double-1>",lambda e:self.reproducir_seleccionada())

            # Progreso
            progreso=tk.Frame(contenedor,bg="#101827")
            progreso.pack(fill="x",pady=(10,0))
            self.barra_progreso=ttk.Scale(progreso,from_=0,to=100,orient="horizontal")
            self.barra_progreso.pack(side="left",fill="x",expand=True)
            self.barra_progreso.bind("<ButtonPress-1>",lambda e:setattr(self,"arrastrando",True))
            self.barra_progreso.bind("<ButtonRelease-1>",self.saltar_a_posicion)
            tk.Label(progreso,textvariable=self.tiempo_texto,fg="#aab8d0",bg="#101827").pack(side="left",padx=8)

            # Botones
            botones=tk.Frame(contenedor,bg="#101827")
            botones.pack(fill="x",pady=10)
            tk.Button(botones,text="Agregar",command=self.agregar_archivos).pack(side="left",padx=2)
            tk.Button(botones,text="Eliminar",command=self.eliminar_seleccionada).pack(side="left",padx=2)
            tk.Button(botones,text="|<",command=self.anterior_cancion).pack(side="left",padx=(16,2))
            tk.Button(botones,text="Play",command=self.reproducir_actual).pack(side="left",padx=2)
            tk.Button(botones,text="Pausa",command=self.alternar_pausa).pack(side="left",padx=2)
            tk.Button(botones,text="Stop",command=self.detener).pack(side="left",padx=2)
            tk.Button(botones,text=">|",command=self.siguiente_cancion).pack(side="left",padx=2)
            tk.Checkbutton(botones,text="Aleatorio",variable=self.aleatorio,fg="#ffffff",bg="#101827",
                           selectcolor="#101827",activebackground="#101827").pack(side="left",padx=(16,2))
            tk.Checkbutton(botones,text="Repetir",variable=self.repetir,fg="#ffffff",bg="#101827",
                           selectcolor="#101827",activebackground="#101827").pack(side="left",padx=2)

            # Volumen
            tk.Label(botones,text="Vol",fg="#aab8d0",bg="#101827").pack(side="left",padx=(16,2))
            ttk.Scale(botones,from_=0,to=1,variable=self.volumen,orient="horizontal",
                      command=self.cambiar_volumen,length=120).pack(side="left")

            self.cambiar_volumen()
            self.ventana.after(500,self.actualizar_progreso)

        def formatear_tiempo(self,segundos):
            segundos=max(0,int(segundos))
            return f"{segundos//60:02d}:{segundos%60:02d}"

        def refrescar_tabla(self,nodos=None):
            """Redibuja la tabla. Cada fila usa el id del nodo como iid."""
            if nodos is None:
                nodos=self.lista.lista_nodos()
            self.tabla.delete(*self.tabla.get_children())
            self.mapa_nodos={}
            for i,nodo in enumerate(nodos,start=1):
                iid=str(id(nodo))
                self.mapa_nodos[iid]=nodo
                self.tabla.insert("","end",iid=iid,values=(i,nodo.titulo))
            self.marcar_actual()

        def marcar_actual(self):
            nodo=self.lista.actual
            if nodo is not None and self.tabla.exists(str(id(nodo))):
                self.tabla.selection_set(str(id(nodo)))
                self.tabla.see(str(id(nodo)))

        def agregar_archivos(self):
            rutas=filedialog.askopenfilenames(title="Selecciona canciones",
                                              filetypes=[("Audio","*.mp3 *.wav *.ogg"),("Todos","*.*")])
            for ruta in rutas:
                self.lista.agregar(ruta)
            if rutas:
                self.refrescar_tabla()
                self.mensaje.set(f"{self.lista.tamaño} canciones en la lista")

        def nodo_seleccionado(self):
            seleccion=self.tabla.selection()
            if not seleccion:
                return None
            return self.mapa_nodos.get(seleccion[0])

        def eliminar_seleccionada(self):
            nodo=self.nodo_seleccionado()
            if nodo is None:
                messagebox.showinfo("Eliminar","Selecciona una cancion primero")
                return
            era_actual=nodo is self.lista.actual
            self.lista.quitar(nodo)
            if era_actual:
                self.detener()
                self.camcion_actual.set("Ninguna canción seleccionada")
            self.refrescar_tabla()
            self.mensaje.set(f"{self.lista.tamaño} canciones en la lista")

        def reproducir_seleccionada(self):
            nodo=self.nodo_seleccionado()
            if nodo is not None:
                self.lista.actual=nodo
                self.reproducir_actual()

        def reproducir_actual(self,inicio=0.0):
            if not self.audio_disponible:
                return
            nodo=self.lista.actual
            if nodo is None:
                messagebox.showinfo("Reproducir","Agrega canciones primero")
                return
            if self.pausado and inicio==0.0 and self.reproduciendo:
                pygame.mixer.music.unpause()
                self.pausado=False
                return
            try:
                pygame.mixer.music.load(nodo.ruta)
                pygame.mixer.music.set_volume(self.volumen.get())
                pygame.mixer.music.play(start=inicio)
            except pygame.error as error:
                messagebox.showerror("Error",f"No se pudo reproducir:\n{error}")
                return
            self.desplazamiento=inicio
            try:
                self.duracion=pygame.mixer.Sound(nodo.ruta).get_length()
            except pygame.error:
                self.duracion=0.0
            self.reproduciendo=True
            self.pausado=False
            self.camcion_actual.set(nodo.titulo)
            self.marcar_actual()

        def alternar_pausa(self):
            if not self.reproduciendo:
                return
            if self.pausado:
                pygame.mixer.music.unpause()
                self.pausado=False
            else:
                pygame.mixer.music.pause()
                self.pausado=True

        def detener(self):
            if self.audio_disponible:
                pygame.mixer.music.stop()
            self.reproduciendo=False
            self.pausado=False
            self.desplazamiento=0.0
            self.tiempo_texto.set("00:00 / 00:00")
            self.barra_progreso.set(0)

        def siguiente_cancion(self):
            if self.lista.esta_vacia():
                return
            if self.aleatorio.get():
                self.lista.actual=self.lista.nodo_aleatorio()
            else:
                self.lista.avanzar()
            self.reproducir_actual()

        def anterior_cancion(self):
            if self.lista.esta_vacia():
                return
            self.lista.retroceder()
            self.reproducir_actual()

        def cambiar_volumen(self,valor=None):
            if self.audio_disponible:
                pygame.mixer.music.set_volume(self.volumen.get())

        def saltar_a_posicion(self,evento=None):
            """Al soltar la barra de progreso, salta a ese punto de la cancion."""
            self.arrastrando=False
            if self.reproduciendo and self.duracion>0:
                destino=self.barra_progreso.get()/100*self.duracion
                self.reproducir_actual(inicio=destino)

        def posicion_actual(self):
            if not self.reproduciendo:
                return 0.0
            return self.desplazamiento+max(0,pygame.mixer.music.get_pos())/1000

        def actualizar_progreso(self):
            """Se ejecuta cada 500 ms: actualiza la barra y avanza al terminar."""
            if self.audio_disponible and self.reproduciendo and not self.pausado:
                if pygame.mixer.music.get_busy():
                    pos=self.posicion_actual()
                    if self.duracion>0 and not self.arrastrando:
                        self.barra_progreso.set(min(100,pos/self.duracion*100))
                    self.tiempo_texto.set(f"{self.formatear_tiempo(pos)} / {self.formatear_tiempo(self.duracion)}")
                else:
                    # La cancion termino sola
                    if self.repetir.get():
                        self.reproducir_actual()
                    else:
                        self.siguiente_cancion()
            self.ventana.after(500,self.actualizar_progreso)

        def buscar(self):
            texto=self.busqueda.get()
            if texto.strip()=="":
                self.refrescar_tabla()
            else:
                self.refrescar_tabla(self.lista.buscar_por_titulo(texto))

        def limpiar_busqueda(self):
            self.busqueda.set("")
            self.refrescar_tabla()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = reproductorMusica(ventana)
    ventana.mainloop()