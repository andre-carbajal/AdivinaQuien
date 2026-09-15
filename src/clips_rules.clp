(deftemplate personaje
  (slot nombre (type STRING))
  (slot mujer (type SYMBOL))
  (slot lentes (type SYMBOL))
  (slot sombrero (type SYMBOL))
  (slot barba (type SYMBOL))
  (slot cabello_negro (type SYMBOL))
  (slot cabello_rubio (type SYMBOL))
  (slot cabello_rojo (type SYMBOL))
  (slot cabello_largo (type SYMBOL)))

(deftemplate candidato
  (slot nombre (type STRING)))

(deftemplate respuesta
  (slot atributo (type SYMBOL))
  (slot valor (type SYMBOL)))

(defrule descartar-mujer
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo mujer) (valor ?valor))
  (personaje (nombre ?nombre) (mujer ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-lentes
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo lentes) (valor ?valor))
  (personaje (nombre ?nombre) (lentes ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-sombrero
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo sombrero) (valor ?valor))
  (personaje (nombre ?nombre) (sombrero ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-barba
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo barba) (valor ?valor))
  (personaje (nombre ?nombre) (barba ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-cabello-negro
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo cabello_negro) (valor ?valor))
  (personaje (nombre ?nombre) (cabello_negro ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-cabello-rubio
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo cabello_rubio) (valor ?valor))
  (personaje (nombre ?nombre) (cabello_rubio ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-cabello-rojo
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo cabello_rojo) (valor ?valor))
  (personaje (nombre ?nombre) (cabello_rojo ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))

(defrule descartar-cabello-largo
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo cabello_largo) (valor ?valor))
  (personaje (nombre ?nombre) (cabello_largo ?otro))
  (test (neq ?otro ?valor))
  =>
  (retract ?c))
