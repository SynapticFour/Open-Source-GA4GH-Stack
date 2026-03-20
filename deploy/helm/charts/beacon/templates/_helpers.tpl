{{- define "beacon.name" -}}
beacon
{{- end }}

{{- define "beacon.fullname" -}}
{{ .Release.Name }}-beacon
{{- end }}
