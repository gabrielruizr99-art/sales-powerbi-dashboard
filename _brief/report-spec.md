# Design Brief — Resumen Ejecutivo

```yaml
Design Brief:
  generated_by: powerbi-report-planning + powerbi-report-design
  contract_version: "1.0"
  mode: brownfield
  approval: approved_by_user_prompt

  audience:
    primary: Dirección comercial y responsables de ventas
    decisions:
      - Evaluar ventas, utilidad y margen del negocio
      - Comparar desempeño actual con el año anterior
      - Identificar categorías, productos y sucursales líderes
    cadence: Revisión ejecutiva periódica

  page:
    existing_page_id: e0a0e56f982e2301aa18
    current_name: "Página 1"
    target_name: "Resumen Ejecutivo"
    width: 1920
    height: 1080
    background: "#F5F7FA"
    layout_grid: 8px
    outer_margin: 32px
    primary_gutter: 24px

  design_direction:
    archetype: Executive Summary — KPI Strip
    tone: Ejecutivo comercial moderno
    signature: Cuadrícula modular estricta con una banda KPI compuesta y contenedores blancos consistentes
    font_family: Segoe UI
    colors:
      page: "#F5F7FA"
      surface: "#FFFFFF"
      header: "#14213D"
      primary: "#2563EB"
      emphasis: "#F59E0B"
      secondary: "#0F766E"
      text_primary: "#1F2937"
      text_secondary: "#64748B"
      comparison: "#94A3B8"
      border: "#E2E8F0"
    effects:
      corner_radius: 8px
      border_width: 1px
      shadows: omitted_for_clarity
      gradients: none

  canvas_regions:
    - name: Encabezado
      x: 0
      y: 0
      width: 1920
      height: 112
      background: "#14213D"
    - name: Panel de filtros
      x: 32
      y: 136
      width: 280
      height: 912
      background: "#FFFFFF"
    - name: Banda KPI
      x: 336
      y: 136
      width: 1552
      height: 160
      background: "#FFFFFF"
    - name: Evolución mensual
      x: 336
      y: 320
      width: 920
      height: 336
      background: "#FFFFFF"
    - name: Ventas por categoría
      x: 1280
      y: 320
      width: 608
      height: 336
      background: "#FFFFFF"
    - name: Top 10 productos
      x: 336
      y: 680
      width: 920
      height: 368
      background: "#FFFFFF"
    - name: Rendimiento por sucursal
      x: 1280
      y: 680
      width: 608
      height: 368
      background: "#FFFFFF"

  header_content:
    title: Resumen Ejecutivo de Ventas
    subtitle: Ferretería | Rendimiento comercial 2024–2026
    freshness_note: Última actualización según los datos del modelo

  filters:
    - title: Año
      field: "bi_ferreteria dim_fecha[anio]"
      style: Dropdown
      placement: { x: 56, y: 216, width: 232, height: 104 }
    - title: Mes
      field: "bi_ferreteria dim_fecha[mes]"
      style: Dropdown
      sort_contract: model_sort_by_mes_numero
      placement: { x: 56, y: 344, width: 232, height: 104 }
    - title: Sucursal
      field: "bi_ferreteria dim_sucursal[sucursal]"
      style: Dropdown
      placement: { x: 56, y: 472, width: 232, height: 104 }
    - title: Canal de venta
      field: "bi_ferreteria dim_canal[canal_venta]"
      style: Dropdown
      placement: { x: 56, y: 600, width: 232, height: 104 }

  visuals:
    - type: cardVisual
      title: Indicadores clave
      placement: { x: 336, y: 136, width: 1552, height: 160 }
      measures:
        - Ventas Netas
        - Utilidad Total
        - Número de Ventas
        - Ticket Promedio
        - Margen %
        - Unidades Vendidas
      display: one_visual_six_callouts
      emphasis: first_two_measures_by_order
    - type: lineChart
      title: Evolución mensual de ventas
      placement: { x: 336, y: 320, width: 920, height: 336 }
      category: "bi_ferreteria dim_fecha[fecha_key]"
      measures: [Ventas Netas, Ventas Año Anterior]
      sort: chronological_ascending
    - type: barChart
      title: Ventas por categoría
      placement: { x: 1280, y: 320, width: 608, height: 336 }
      category: "bi_ferreteria dim_producto[categoria]"
      measures: [Ventas Netas]
      sort: value_descending
    - type: barChart
      title: Top 10 productos por ventas
      placement: { x: 336, y: 680, width: 920, height: 368 }
      category: "bi_ferreteria dim_producto[producto]"
      measures: [Ventas Netas]
      filter: top_10_by_sum_fact_ventas_venta_neta
      sort: value_descending
    - type: clusteredBarChart
      title: Rendimiento por sucursal
      placement: { x: 1280, y: 680, width: 608, height: 368 }
      category: "bi_ferreteria dim_sucursal[sucursal]"
      measures: [Ventas Netas, Utilidad Total]
      sort: ventas_netas_descending

  color_map:
    Ventas Netas: "#2563EB"
    Ventas Año Anterior: "#94A3B8"
    Utilidad Total: "#0F766E"
    emphasis: "#F59E0B"

  interaction_contract:
    slicers_filter_all_data_visuals: true
    natural_cross_filtering: true
    custom_visuals: false
    maps: false
    technical_keys_visible: false

  accessibility:
    minimum_text_contrast: WCAG_AA_target
    titles_in_spanish: true
    alt_text_required: true
    visual_headers: hidden_in_reading_view

  implementation_constraints:
    preserve_pbir_version: "4.0"
    preserve_existing_schemas: true
    preserve_dataset_reference: "../sales-powerbi.SemanticModel"
    semantic_model_changes: forbidden
    page_action: rename_existing_page
    deprecated_visuals: forbidden
    custom_visuals: forbidden

  space_audit:
    page_area_px2: 2073600
    occupied_region_area_px2: 1866240
    occupied_ratio: 0.90
    intentional_whitespace_ratio: 0.10
    overlap_expected: false
    all_coordinates_on_8px_grid: true

  validation_plan:
    - validate_after_page_shell
    - validate_after_filters_and_kpis
    - validate_after_charts
    - desktop_reload
    - screenshot_review
    - semantic_model_digest_comparison
```

## Nota de implementación

El visual KPI será un único `cardVisual` moderno con seis proyecciones en el rol `Data`. La jerarquía visual se establece mediante el orden de las medidas, colocando Ventas Netas y Utilidad Total primero. El resaltado dinámico de la categoría líder no se codificará si exige una medida de ranking nueva, ya que el modelo semántico es de solo lectura para esta tarea.
