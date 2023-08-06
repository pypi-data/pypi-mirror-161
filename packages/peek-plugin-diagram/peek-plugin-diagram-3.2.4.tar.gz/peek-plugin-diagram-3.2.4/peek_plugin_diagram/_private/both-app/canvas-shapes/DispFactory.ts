import { DispBase } from "./DispBase";
import { DispPolyline } from "./DispPolyline";
import { DispPolygon } from "./DispPolygon";
import { DispText } from "./DispText";
import { DispEllipse } from "./DispEllipse";
import { DispGroupPointer } from "./DispGroupPointer";
import { DispGroup } from "./DispGroup";
import { DispNull } from "./DispNull";

export class DispFactory {
    private static _typeMapInit = false;
    private static _typeMap = {};

    // Lazy instantiation, because the string types are defined elsewhere
    private static get typeMap() {
        if (!DispFactory._typeMapInit) {
            DispFactory._typeMapInit = true;
            DispFactory._typeMap[DispBase.TYPE_DT] = [DispText];
            DispFactory._typeMap[DispBase.TYPE_DPG] = [DispPolygon];
            DispFactory._typeMap[DispBase.TYPE_DPL] = [DispPolyline];
            DispFactory._typeMap[DispBase.TYPE_DE] = [DispEllipse];
            DispFactory._typeMap[DispBase.TYPE_DG] = [DispGroup];
            DispFactory._typeMap[DispBase.TYPE_DGP] = [DispGroupPointer];
            DispFactory._typeMap[DispBase.TYPE_DN] = [DispNull];
        }

        return DispFactory._typeMap;
    }

    static wrapper(disp): any {
        return DispFactory.typeMap[disp._tt][0];
    }
}
