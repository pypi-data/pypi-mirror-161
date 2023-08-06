import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import {
    DispCurvedTextT,
    CurvedTextHorizontalAlign,
    CurvedTextVerticalAlign,
    DispCurvedText,
} from "../canvas-shapes/DispCurvedText";
import { pointToPixel } from "../DiagramUtil";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { DispColor, DispTextStyle } from "@peek/peek_plugin_diagram/lookups";
import { DispPolygon } from "../canvas-shapes/DispPolygon";

interface SubPathIndexRange {
    isReversed: boolean;
    rightExclusiveBoundaryIndex: number;
}

interface ProcessedPath {
    subPaths: number[][];
    pathLength: number;
}

interface CurvedTextPathDrawingContext {
    distanceOfSegment: number;
    distanceConsumed: number;
    pathIndex: number;
    nextPoint?: {
        location: PointI;
        angle: number;
    };
}

export class PeekDispRenderDelegateCurvedText extends PeekDispRenderDelegateABC {
    private textMeasureCtx;

    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);

        // Create a canvas element for measuring text
        let canvas = document.createElement("canvas");
        this.textMeasureCtx = canvas.getContext("2d");
    }

    updateBounds(disp: DispBaseT, zoom: number): void {
        this.drawAndCalcBounds(
            <DispCurvedTextT>disp,
            this.textMeasureCtx,
            zoom,
            true
        );
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    draw(
        disp: DispCurvedTextT,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE
    ) {
        this.drawAndCalcBounds(disp, ctx, zoom, false);
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        // PeekDispRenderDelegatePoly.drawSelectedPolygon
        let geom = DispPolygon.geom(disp);

        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // DRAW THE SELECTED BOX
        let bounds = PeekCanvasBounds.fromGeom(geom);

        // Move the selection line a bit away from the object
        let offset = (selectionConfig.width + selectionConfig.lineGap) / zoom;

        let twiceOffset = 2 * offset;
        let x = bounds.x - offset;
        let y = bounds.y - offset;
        let w = bounds.w + twiceOffset;
        let h = bounds.h + twiceOffset;

        ctx.dashedRect(x, y, w, h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        // PeekDispRenderDelegatePoly.drawEditHandles
        ctx.fillStyle = this.config.editor.selectionHighlightColor;
        const handles = this.handles(disp);
        for (const handle of handles) {
            const b = handle.box;
            ctx.beginPath();
            ctx.arc(b.x + b.w / 2, b.y + b.h / 2, b.h / 2, 0, 2 * Math.PI);
            ctx.fill();
        }
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    private drawAndCalcBounds(
        disp: DispCurvedTextT,
        ctx,
        zoom: number,
        updateBounds: boolean
    ) {
        let textStyle = DispCurvedText.textStyle(disp);
        let fillColor = DispCurvedText.color(disp);

        // Null colors are also not drawn
        fillColor = fillColor && fillColor.color ? fillColor : null;

        // TODO, Draw a box around the text, based on line style

        let horizontalStretchFactor = DispCurvedText.horizontalStretch(disp);
        let textHeight = DispCurvedText.height(disp);

        let fontSize = textStyle.fontSize * textStyle.scaleFactor;

        if (textHeight != null) fontSize = textHeight;

        const font =
            (textStyle.fontStyle || "") +
            " " +
            fontSize +
            "px " +
            textStyle.fontName;

        let lineHeight = pointToPixel(fontSize);

        let textAlign = null;
        let horizontalAlignEnum = DispCurvedText.horizontalAlign(disp);
        if (horizontalAlignEnum == CurvedTextHorizontalAlign.left)
            textAlign = "start";
        else if (horizontalAlignEnum == CurvedTextHorizontalAlign.center)
            textAlign = "center";
        else if (horizontalAlignEnum == CurvedTextHorizontalAlign.right)
            textAlign = "end";

        let textBaseline = null;
        let verticalAlignEnum = DispCurvedText.verticalAlign(disp);
        if (verticalAlignEnum == CurvedTextVerticalAlign.top)
            textBaseline = "top";
        else if (verticalAlignEnum == CurvedTextVerticalAlign.center)
            textBaseline = "middle";
        else if (verticalAlignEnum == CurvedTextVerticalAlign.bottom)
            textBaseline = "bottom";

        const centerX = DispCurvedText.centerPointX(disp);
        const centerY = DispCurvedText.centerPointY(disp);

        // save state
        ctx.save();
        let singleLineHeight = this.drawCurvedTexts(
            ctx,
            textAlign,
            textBaseline,
            font,
            textStyle,
            zoom,
            horizontalStretchFactor,
            updateBounds,
            disp,
            lineHeight,
            fillColor
        );

        // restore to original state
        ctx.restore();

        if (updateBounds) {
            if (horizontalAlignEnum == CurvedTextHorizontalAlign.left)
                disp.bounds.x = centerX;
            else if (horizontalAlignEnum == CurvedTextHorizontalAlign.center)
                disp.bounds.x = centerX - disp.bounds.w / 2;
            else if (horizontalAlignEnum == CurvedTextHorizontalAlign.right)
                disp.bounds.x = centerX - disp.bounds.w;

            if (verticalAlignEnum == CurvedTextVerticalAlign.top)
                disp.bounds.y = centerY;
            else if (verticalAlignEnum == CurvedTextVerticalAlign.center)
                disp.bounds.y = centerY - singleLineHeight / 2;
            else if (verticalAlignEnum == CurvedTextVerticalAlign.bottom)
                disp.bounds.y = centerY - singleLineHeight;
        }
    }

    private calculateDistance2D(
        x1: number,
        y1: number,
        x2: number,
        y2: number
    ): number {
        const dx = x2 - x1;
        const dy = y2 - y1;
        return Math.sqrt(dx * dx + dy * dy);
    }

    private calculateRotationAngle(y, x) {
        return Math.atan2(y, x);
    }

    private reversePath(path: number[]) {
        const reversedPath = [];
        for (let i = path.length - 2; i >= 0; i -= 2) {
            reversedPath.push(path[i]);
            reversedPath.push(path[i + 1]);
        }
        return reversedPath;
    }

    private preprocessPath(path: number[]): ProcessedPath {
        // check if the path is valid
        if (path.length % 2 != 0) {
            throw new Error(
                "path should be an 1-dimension array of coordinates of x and y."
            );
        }

        const segmentLengths: number[] = [];
        let pathLength: number = 0;
        const angles: number[] = [];
        const reverseDirectionOfXAxisFlags: boolean[] = [];
        const subPathIndexRanges: SubPathIndexRange[] = [];

        const subPaths = [];

        // loop over each segment of the path
        for (let i = 2; i < path.length; i += 2) {
            const previousX = path[i - 2];
            const previousY = path[i - 1];
            const thisX = path[i];
            const thisY = path[i + 1];

            const segmentDistance = this.calculateDistance2D(
                previousX,
                previousY,
                thisX,
                thisY
            );

            segmentLengths.push(segmentDistance);
            pathLength += segmentDistance;

            // add angle of two segments that forms
            const angle = this.calculateRotationAngle(
                thisY - previousY,
                thisX - previousX
            );
            angles.push(angle);

            // check whether the text is straight up or up-side-down
            //  angles in quadrant II or III need normalising
            //  https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/rotate#syntax
            //                     -90
            //                     │
            //                     │
            //                     │
            //                II   │     I
            //                     │
            //                     │
            // 180/-180 ───────────┼──────────── 0 x
            //                     │
            //                     │
            //                III  │     IV
            //                     │
            //                     │
            //                     │
            //                     │
            //                     90
            //                     y

            // normalisation ranges
            //  90   to  180 and -90    to  -180 in degree
            // 1/2Pi to  1Pi and -1/2Pi to  -1Pi in radian

            // normalisation shortcut: make angles in quadrant III and IV
            //  flipped horizontally into quadrant II and I
            const absoluteAngle = Math.abs(angle);
            reverseDirectionOfXAxisFlags.push(
                // check if it's in quadrant II
                absoluteAngle > Math.PI / 2 && absoluteAngle <= Math.PI
            );
        }

        // check segments direction
        if (
            // segments go against with x-axis only
            reverseDirectionOfXAxisFlags.includes(true) &&
            !reverseDirectionOfXAxisFlags.includes(false)
        ) {
            // flipped/hanging texts can be fixed by
            // drawing the text sequentially along the reversed path
            const reversedPath = this.reversePath(path);
            subPaths.push(reversedPath);
        } else if (
            // segments go along and against x-axis
            reverseDirectionOfXAxisFlags.includes(false) &&
            reverseDirectionOfXAxisFlags.includes(true)
        ) {
            // handle mixed directions in path

            // find groups of continuous segments that go to the same direction
            //  this finds index range of coordinates in each group
            let lastSameDirectionAngleIndex: number = 0;
            for (let i = 0; i < reverseDirectionOfXAxisFlags.length; ++i) {
                const isReversed =
                    reverseDirectionOfXAxisFlags[lastSameDirectionAngleIndex];

                // give a range from the last angle to the last point of path
                if (i == reverseDirectionOfXAxisFlags.length - 1) {
                    subPathIndexRanges.push({
                        isReversed: isReversed,
                        rightExclusiveBoundaryIndex: path.length,
                    });
                    break;
                }

                if (
                    // this goes to a different direction from last angle
                    reverseDirectionOfXAxisFlags[i] !=
                    reverseDirectionOfXAxisFlags[lastSameDirectionAngleIndex]
                ) {
                    // find last point of the segment in this.path
                    const rightExclusiveBoundary =
                        2 * lastSameDirectionAngleIndex;
                    subPathIndexRanges.push({
                        isReversed: isReversed,
                        rightExclusiveBoundaryIndex: rightExclusiveBoundary,
                    });
                }
                // update last seen direction
                lastSameDirectionAngleIndex = i;
            }

            // generate subpaths based on index ranges
            for (let i = 0; i < subPathIndexRanges.length; ++i) {
                // make first subpath from the start of this.path
                const inclusiveStartPointXIndex =
                    i == 0
                        ? 0
                        : // make other subpaths starts inclusively
                          //  from previous right exclusive boundary
                          subPathIndexRanges[i - 1].rightExclusiveBoundaryIndex;
                const exclusiveEndPointXIndex =
                    subPathIndexRanges[i].rightExclusiveBoundaryIndex;

                // reverse the sub path if flagged as reversed
                const subPath = subPathIndexRanges[i].isReversed
                    ? this.reversePath(
                          // Array.slice treats the boundaries
                          //  as [leftIndex, rightIndex)
                          path.slice(
                              inclusiveStartPointXIndex,
                              exclusiveEndPointXIndex
                          )
                      )
                    : path.slice(
                          inclusiveStartPointXIndex,
                          exclusiveEndPointXIndex
                      );
                subPaths.push(subPath);
            }
        } else if (
            reverseDirectionOfXAxisFlags.includes(false) &&
            !reverseDirectionOfXAxisFlags.includes(true)
        ) {
            // whole path is along with x-axis
            // draw along with the original path
            subPaths.push(path);
        }

        return { subPaths: subPaths, pathLength: pathLength };
    }

    private locateNextCharacter(
        distanceFromStart: number,
        path: number[],
        curvedTextPathDrawingContext: CurvedTextPathDrawingContext
    ): CurvedTextPathDrawingContext {
        {
            // get states from context
            let _distanceOfSegment =
                curvedTextPathDrawingContext.distanceOfSegment;
            let _distanceConsumed =
                curvedTextPathDrawingContext.distanceConsumed;
            let _pathIndex = curvedTextPathDrawingContext.pathIndex;

            //  if next drawing position fits on this segment of path
            if (
                !_distanceOfSegment ||
                _distanceConsumed + _distanceOfSegment < distanceFromStart
            ) {
                // search the segment that fits the position to draw next
                for (; _pathIndex < path.length; ) {
                    _distanceOfSegment = this.calculateDistance2D(
                        path[_pathIndex - 2],
                        path[_pathIndex - 1],
                        path[_pathIndex],
                        path[_pathIndex + 1]
                    );
                    if (
                        _distanceConsumed + _distanceOfSegment >
                        distanceFromStart
                    )
                        // segment found and stop searching on the path
                        break;
                    // go to the next segment on path
                    _pathIndex += 2;
                    // updated used distance
                    _distanceConsumed += _distanceOfSegment;
                    // stop searching if all segmentLengths are used
                    if (_pathIndex >= path.length) break;
                }
            }

            // new segment for drawing has found from above

            const distanceFromLastKeyPoint =
                distanceFromStart - _distanceConsumed;
            // use last key point on path if searching overshoots the path
            if (_pathIndex >= path.length) {
                _pathIndex = path.length - 2;
            }

            let x, y;
            // new drawing is on keypoint
            if (!distanceFromLastKeyPoint) {
                // get {x,y} of the previous point on path
                x = path[_pathIndex - 2];
                y = path[_pathIndex - 1];
            } else {
                // get {x,y} between key points with a ratio of new distance
                x =
                    path[_pathIndex - 2] +
                    ((path[_pathIndex] - path[_pathIndex - 2]) *
                        distanceFromLastKeyPoint) /
                        _distanceOfSegment;
                y =
                    path[_pathIndex - 1] +
                    ((path[_pathIndex + 1] - path[_pathIndex - 1]) *
                        distanceFromLastKeyPoint) /
                        _distanceOfSegment;
            }

            const deltaY = path[_pathIndex + 1] - path[_pathIndex - 1];
            const deltaX = path[_pathIndex] - path[_pathIndex - 2];
            const rotationAngle = this.calculateRotationAngle(deltaY, deltaX);

            return {
                distanceOfSegment: _distanceOfSegment,
                distanceConsumed: _distanceConsumed,
                pathIndex: _pathIndex,
                nextPoint: { location: { x: x, y: y }, angle: rotationAngle },
            };
        }
    }

    private drawCurvedTexts(
        ctx,
        textAlign,
        textBaseline,
        font: string,
        fontStyle: DispTextStyle,
        zoom: number,
        horizontalStretchFactor: number,
        updateBounds: boolean,
        disp: DispCurvedTextT,
        lineHeight: number,
        fillColor: DispColor
    ): number {
        // set up text styling
        ctx.textAlign = textAlign;
        ctx.textBaseline = textBaseline;
        ctx.font = font;

        if (!fontStyle.scalable) {
            let unscale = 1.0 / zoom;
            ctx.scale(unscale, unscale);
        }

        if (horizontalStretchFactor != 1) {
            ctx.scale(horizontalStretchFactor, 1);
        }

        // Bounds can get serliased in branches, so check to see if it's actually the
        // class or just the restored object that it serialises to.
        if (updateBounds) {
            disp.bounds = new PeekCanvasBounds();
            disp.bounds.w = 0;
        }

        // draw

        // cache all text measurement to workaround for performance
        //  https://bugzilla.mozilla.org/show_bug.cgi?id=527386#c19
        let chars = DispCurvedText.text(disp).replace("\n", " ");
        const textWidth = ctx.measureText(chars).width;
        const measureTextLengthMap: { [text: string]: number } = {};
        measureTextLengthMap[chars] = textWidth;

        // this works like space-around in flexbox
        const spacingInBetween =
            DispCurvedText.spacingBetweenTexts(disp) === undefined
                ? DispCurvedText.spacingBetweenTexts(disp) / zoom // from disp
                : DispCurvedText.textStyle(disp).spacingBetweenTexts / zoom; // from text style
        const horizontalMargin = spacingInBetween / 4;
        const marginTotalWidth = horizontalMargin * 2;

        // draw text(s) on each sub-path where all turns of the subpath are towards
        //  the same direction of x axis i.e. west or east
        const processedPath = this.preprocessPath(disp.g);

        for (const subPath of processedPath.subPaths) {
            // const textPositioner = new TextPositioner(chars, subPath);
            const processedSubPath = this.preprocessPath(subPath);
            let curvedTextPathDrawingContext: CurvedTextPathDrawingContext = {
                distanceOfSegment: 0,
                distanceConsumed: 0,
                pathIndex: 2,
            };

            let spareDistance: number;
            let repeatCount: number;
            let marginAddable: boolean;

            // check if text needs repeating with proper margins and spacings
            // when path is too short to fit text
            if (processedSubPath.pathLength < textWidth) {
                //  skip the whole length - draw nothing
                repeatCount = 0;
                spareDistance = processedSubPath.pathLength;
                marginAddable = false;
            }
            // when path can fit at least one drawing of text
            // path can repeat text drawings
            //  i.e. >= 2 drawings of text with spacing inbetween
            else if (
                processedSubPath.pathLength >=
                2 * textWidth + 2 * marginTotalWidth + spacingInBetween
            ) {
                repeatCount = Math.floor(
                    (processedSubPath.pathLength + spacingInBetween) /
                        (marginTotalWidth + textWidth + spacingInBetween)
                );
                spareDistance =
                    processedSubPath.pathLength -
                    repeatCount * (marginTotalWidth + textWidth) -
                    (repeatCount - 1) * spacingInBetween;
                marginAddable = true;
            } else {
                // when path can fit one drawing of text only
                //  with or without margins
                // draw the text in the middle
                repeatCount = 1;
                spareDistance = processedSubPath.pathLength - textWidth;
                marginAddable = false;
            }

            // start drawing at the location where the text(s) are centered
            let distanceFromStartPoint = spareDistance / 2;

            // repeat text until it occupies the whole length of the path
            for (let i = 0; i < repeatCount; ++i) {
                // add distance used for left margin
                if (marginAddable) distanceFromStartPoint += horizontalMargin;

                // draw each character of the text
                for (let charIndex = 0; charIndex < chars.length; ++charIndex) {
                    const char = chars[charIndex];
                    const charWidth =
                        char in measureTextLengthMap
                            ? measureTextLengthMap.char
                            : ctx.measureText(char).width;

                    curvedTextPathDrawingContext = this.locateNextCharacter(
                        distanceFromStartPoint + charWidth / 2,
                        subPath,
                        curvedTextPathDrawingContext
                    );
                    ctx.save();

                    ctx.textAlign = "center";
                    ctx.translate(
                        curvedTextPathDrawingContext.nextPoint.location.x,
                        curvedTextPathDrawingContext.nextPoint.location.y
                    );
                    ctx.rotate(curvedTextPathDrawingContext.nextPoint.angle);

                    // TODO: stroke text
                    if (fillColor) {
                        ctx.fillStyle = fillColor.color;
                        ctx.fillText(char, 0, 0);
                    }
                    ctx.restore();
                    // add distance used for the character
                    distanceFromStartPoint += charWidth;
                }
                // add distance used for right margin
                if (marginAddable) distanceFromStartPoint += horizontalMargin;
                // add spacing between text repeats
                if (i < repeatCount) distanceFromStartPoint += spacingInBetween;
            }
        }

        let singleLineHeight = lineHeight / zoom;
        if (updateBounds) {
            disp.bounds.h = singleLineHeight * chars.length;
        }
        return singleLineHeight;
    }
}
