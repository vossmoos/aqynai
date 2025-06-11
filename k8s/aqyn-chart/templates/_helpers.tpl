{{/*
Expand the name of the chart.
*/}}
{{- define "aqyn.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "aqyn.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "aqyn.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "aqyn.labels" -}}
helm.sh/chart: {{ include "aqyn.chart" . }}
{{ include "aqyn.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "aqyn.selectorLabels" -}}
app.kubernetes.io/name: {{ include "aqyn.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
PostgreSQL labels
*/}}
{{- define "aqyn.postgres.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: postgres
{{- end }}

{{/*
PostgreSQL selector labels
*/}}
{{- define "aqyn.postgres.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: postgres
{{- end }}

{{/*
MinIO labels
*/}}
{{- define "aqyn.minio.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: minio
{{- end }}

{{/*
MinIO selector labels
*/}}
{{- define "aqyn.minio.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: minio
{{- end }}

{{/*
Dagster Webserver labels
*/}}
{{- define "aqyn.dagster-webserver.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: dagster-webserver
{{- end }}

{{/*
Dagster Webserver selector labels
*/}}
{{- define "aqyn.dagster-webserver.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: dagster-webserver
{{- end }}

{{/*
Dagster Daemon labels
*/}}
{{- define "aqyn.dagster-daemon.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: dagster-daemon
{{- end }}

{{/*
Dagster Daemon selector labels
*/}}
{{- define "aqyn.dagster-daemon.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: dagster-daemon
{{- end }}

{{/*
Hasura labels
*/}}
{{- define "aqyn.hasura.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: hasura
{{- end }}

{{/*
Hasura selector labels
*/}}
{{- define "aqyn.hasura.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: hasura
{{- end }}

{{/*
API labels
*/}}
{{- define "aqyn.api.labels" -}}
{{ include "aqyn.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{/*
API selector labels
*/}}
{{- define "aqyn.api.selectorLabels" -}}
{{ include "aqyn.selectorLabels" . }}
app: aqyn-api
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "aqyn.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "aqyn.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}