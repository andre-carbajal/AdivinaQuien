(deftemplate rasgo
  (slot personaje (type STRING))
  (slot atributo (type SYMBOL))
  (slot valor (type SYMBOL)))

(deftemplate candidato
  (slot nombre (type STRING)))

(deftemplate respuesta
  (slot atributo (type SYMBOL))
  (slot valor (type SYMBOL)))

(deftemplate descartado
  (slot nombre (type STRING))
  (slot atributo (type SYMBOL))
  (slot esperado (type SYMBOL))
  (slot recibido (type SYMBOL)))

(defrule descartar-incompatible
  ?c <- (candidato (nombre ?nombre))
  (respuesta (atributo ?atributo) (valor ?recibido))
  (rasgo (personaje ?nombre)
         (atributo ?atributo)
         (valor ?esperado))
  (test (neq ?esperado ?recibido))
  =>
  (retract ?c)
  (assert (descartado
    (nombre ?nombre)
    (atributo ?atributo)
    (esperado ?esperado)
    (recibido ?recibido))))
