/** Diagram Config Service
 *
 * This allows other plugins to configure the diagram thats currently shown.
 *
 */
export abstract class DiagramConfigService {
    abstract setLayerVisible(
        modelSetKey: string,
        layerName: string,
        visible: boolean
    ): void;

    abstract setUsePolylineEdgeColors(enabled: boolean): void;

    abstract setToolbarVisible(enabled: boolean): void;
}
