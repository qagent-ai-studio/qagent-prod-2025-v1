import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Star, MessageSquare } from 'lucide-react'

export default function SurveyForm() {
  const [formState, setFormState] = useState({
    score: 0,
    reason: '',
    magicWish: ''
  })
  const [hover, setHover] = useState(0)   // ⭐ valor en hover
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)

  // 👉 Ajusta validación para score
  const validateForm = () => {
    const newErrors = {}
    if (!formState.score || formState.score < 1 || formState.score > 10) {
      newErrors.score = 'Debes elegir un valor del 1 al 10'
    }
    if (!formState.reason.trim()) {
      newErrors.reason = 'Por favor cuéntanos brevemente el porqué de tu respuesta'
    }
    if (!formState.magicWish.trim()) {
      newErrors.magicWish = 'Por favor responde esta pregunta'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return
    setSubmitting(true)
    try {
      const result = await callAction({
        name: "submit_survey",
        payload: formState
      })
      if (result.success) {
        setSubmitSuccess(true)
        sendUserMessage("✅ ¡Gracias por responder nuestra encuesta!")
      } else {
        setErrors({ form: 'Error al enviar la encuesta. Inténtalo de nuevo.' })
      }
    } catch {
      setErrors({ form: 'Error al procesar la solicitud.' })
    } finally {
      setSubmitting(false)
    }
  }

  if (submitSuccess) {
    return (
      <Card className="w-full max-w-lg mx-auto text-center">
        <CardContent className="pt-6">
          <h3 className="text-lg font-medium mb-2 text-gray-100">¡Encuesta enviada!</h3>
          <p className="text-sm text-gray-300">
            Agradecemos mucho tu tiempo y tu feedback 🙌
          </p>
          <Button onClick={deleteElement} className="mt-4">Cerrar</Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Encuesta Rápida
        </CardTitle>
      </CardHeader>
      <CardContent>
        {errors.form && (
          <div className="bg-red-900/20 border border-red-500/30 text-red-300 p-3 rounded-md mb-4 text-sm">
            {errors.form}
          </div>
        )}

        <div className="space-y-4">
          {/* Pregunta 1 con estrellas */}
          <div>
            <Label className="text-sm font-medium flex items-center gap-2 block mb-3">
              <Star className="h-4 w-4" /> En una escala del 1 al 10, ¿qué tan probable es que recomiendes este Agente IA a un colega?
            </Label>
            <div className="flex justify-between w-full">
              {Array.from({ length: 10 }, (_, i) => i + 1).map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setFormState({ ...formState, score: num })}
                  onMouseEnter={() => setHover(num)}
                  onMouseLeave={() => setHover(0)}
                  className="focus:outline-none"
                >
                  <Star
                    className={`h-7 w-7 transition-colors ${
                      num <= (hover || formState.score)
                        ? num <= 6
                          ? "text-red-500 fill-red-500"
                          : num <= 8
                          ? "text-yellow-500 fill-yellow-500"
                          : "text-green-500 fill-green-500"
                        : "text-gray-300"
                    }`}
                  />
                </button>
              ))}
            </div>
            {errors.score && <p className="text-red-500 text-xs mt-1">{errors.score}</p>}
          </div>

          {/* Pregunta 2 */}
          <div>
            <Label htmlFor="reason" className="text-sm font-medium block mb-3" >
              Cuéntanos brevemente el porqué de tu respuesta
            </Label>
            <Textarea
              id="reason"
              name="reason"
              rows={3}
              placeholder="Tu comentario..."
              value={formState.reason}
              onChange={(e) => setFormState({ ...formState, reason: e.target.value })}
              className={errors.reason ? "border-red-500" : ""}
            />
            {errors.reason && <p className="text-red-500 text-xs mt-1">{errors.reason}</p>}
          </div>

          {/* Pregunta 3 */}
          <div>
            <Label htmlFor="magicWish" className="text-sm font-medium block mb-3">
              Si tuvieras un Agente IA ideal capaz de hacer algo mágico que ninguna otra solución puede, ¿qué sería y cómo mejoraría tu día a día?
            </Label>
            <Textarea
              id="magicWish"
              name="magicWish"
              rows={4}
              placeholder="Escribe tu idea..."
              value={formState.magicWish}
              onChange={(e) => setFormState({ ...formState, magicWish: e.target.value })}
              className={errors.magicWish ? "border-red-500" : ""}
            />
            {errors.magicWish && <p className="text-red-500 text-xs mt-1">{errors.magicWish}</p>}
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={deleteElement}>Cancelar</Button>
        <Button onClick={handleSubmit} disabled={submitting} className="gap-2">
          {submitting ? "Enviando..." : "Enviar Encuesta"}
        </Button>
      </CardFooter>
    </Card>
  )
}
