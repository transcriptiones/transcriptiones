/*
  SimpleRange v1.0.4 | Repo: https://github.com/maxshuty/accessible-web-components/src/components/simpleRange.js
  By Max Poshusta | https://github.com/maxshuty | https://www.linkedin.com/in/maxposhusta/
*/

// Object containing common CSS styles so we can change them in once place
const cssHelpers = Object.freeze({
  sliderBackgroundColor: 'tomato',
  sliderBorderColor: '#8b8b8b',
  sliderBorderRadius: '4px',
  sliderCircleSize: 20,
  sliderCircleBackgroundColor: '#ffffff',
  sliderCircleFocusColor: '#0074cc',
  sliderCommonSize: '0.5em',
});

const constants = Object.freeze({
  MIN: 'min',
  MAX: 'max',
  SLIDER_ID: 'minMaxSlider',
  MIN_LABEL_ID: `minLabel`,
  MAX_LABEL_ID: `maxLabel`,
  RANGE_STOPPED_EVENTS: ['mouseup', 'touchend', 'keyup'],
  CUSTOM_EVENT_TO_EMIT_NAME: 'range-changed',
  RANGE_INPUT_DATA_LABEL_MIN: 'data-range-input-label-min',
  RANGE_INPUT_DATA_LABEL_MAX: 'data-range-input-label-max',
});

const template = document.createElement('template');
template.innerHTML = `
    <style>
      .min-max-slider { 
        position: relative;
        width: 100%;
        text-align: center;
      }
         
      .min-max-slider > label {
        position: absolute;
        left: -10000px;
        top: auto;
        width: 1px;
        height: 1px;
        overflow: hidden;
      }
        
      .min-max-slider > .legend {
        display: flex;
        justify-content: space-between;
      }
        
      .min-max-slider > .legend > * {
        font-size: small;
      }
        
      .min-max-slider > .range-input {
        --sliderColor: ${cssHelpers.sliderCircleBackgroundColor};
        --sliderBorderColor: ${cssHelpers.sliderBorderColor};
        --sliderFocusBorderColor: ${cssHelpers.sliderCircleFocusColor};
        cursor: pointer;
        position: absolute;
        -webkit-appearance: none;
        outline: none !important;
        background: transparent;
        background-image: linear-gradient(to bottom, transparent 0%, transparent 30%, ${
          cssHelpers.sliderBackgroundColor
        } 30%, ${
  cssHelpers.sliderBackgroundColor
} 60%, transparent 60%, transparent 100%);
      }
        
      .min-max-slider > .range-input::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: ${cssHelpers.sliderCircleSize}px;
        height: ${cssHelpers.sliderCircleSize}px;
        background-color: var(--sliderColor);
        cursor: pointer;
        border: 1px solid var(--sliderBorderColor);
        border-radius: 100%;
      }
      
      .min-max-slider > .range-input::-moz-range-thumb {
        width: ${cssHelpers.sliderCircleSize}px;
        height: ${cssHelpers.sliderCircleSize}px;
        background-color: var(--sliderColor);
        cursor: pointer;
        border: 1px solid var(--sliderBorderColor);
        border-radius: 100%;
      } 
        
      .min-max-slider > .range-input::-webkit-slider-runnable-track,  
      .min-max-slider > .range-input::-moz-range-track {
        cursor: pointer;
      }
        
      .min-max-slider > .range-input:focus::-webkit-slider-thumb {
        /* Accessible border on focus */
        border: 2px solid var(--sliderFocusBorderColor);
      }

      .min-max-slider > .range-input:focus::-moz-range-thumb {
          /* Accessible border on focus */
          border: 2px solid var(--sliderFocusBorderColor);
      }
        
      span.value {
        height: 1.7em;
        font-weight: bold;
        display: inline-block;
      }
    
      span.value.upper::before {
        .range-input-dash-icon {
          padding: 0 ${cssHelpers.sliderCommonSize};
        }

        .range-input-label {
            border: 5px solid ${cssHelpers.sliderBorderColor};
            border-radius: ${cssHelpers.sliderBorderRadius};
            padding: ${cssHelpers.sliderCommonSize};
        }
      </style>
      
      <div id="${constants.SLIDER_ID}" class="min-max-slider"></div>
  `;

class SimpleRange extends HTMLElement {
  constructor() {
    super();

    // Setting these variables so that we can clean up the event listeners
    // on the disconnectedCallback, you can't just remove an anonymous function
    // otherwise
    this.emitRangeSelection = () => this.emitRange();
    this.onRangeInput = (el) => this.update(el.target);

    // Setting up the shadow DOM
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }

  static get observedAttributes() {
    return ['min-label', 'max-label', 'min-range', 'max-range', 'min', 'max'];
  }

  get sliderId() {
    return this.getAttribute('id');
  }

  get minRange() {
    return (
      parseInt(this.getAttribute('min-range')) ||
      parseInt(this.getAttribute('min')) ||
      1
    );
  }
  set minRange(minimumRange) {
    this.setAttribute('min-range', minimumRange);
    this.setAttribute('min', minimumRange);
  }

  get maxRange() {
    return (
      parseInt(this.getAttribute('max-range')) ||
      parseInt(this.getAttribute('max')) ||
      0
    );
  }
  set maxRange(maximumRange) {
    this.setAttribute('max-range', maximumRange);
    this.setAttribute('max', maximumRange);
  }

  get numberOfLegendItemsToShow() {
    // If the consumer has specified the number of items to show and the number is at least 2
    // then we return that number, else we return 2 as there always needs to be at least 2
    const numOfLegendItems = parseInt(
      this.getAttribute('number-of-legend-items-to-show')
    );
    return numOfLegendItems && numOfLegendItems > 1 ? numOfLegendItems : 2;
  }

  get hideLegend() {
    return this.hasAttribute('hide-legend');
  }

  get hideLabel() {
    return this.hasAttribute('hide-label');
  }

  get inputsForLabels() {
    return this.hasAttribute('inputs-for-labels');
  }

  get sliderColor() {
    return this.getAttribute('slider-color');
  }

  get circleColor() {
    return this.getAttribute('circle-color');
  }

  get circleBorderColor() {
    return this.getAttribute('circle-border-color');
  }

  get circleFocusBorderColor() {
    return this.getAttribute('circle-focus-border-color');
  }

  get eventNameToEmitOnChange() {
    return (
      this.getAttribute('event-name-to-emit-on-change') ||
      constants.CUSTOM_EVENT_TO_EMIT_NAME
    );
  }

  attributeChangedCallback(name, oldValue, newValue) {
    switch (name) {
      case 'min-label':
        if (!newValue) {
          return;
        }

        const minLabel = this.getEl(constants.MIN_LABEL_ID);
        if (!minLabel) {
          return;
        }

        minLabel.innerText = newValue;
        break;
      case 'max-label':
        if (!newValue) {
          return;
        }

        const maxLabel = this.getEl(constants.MAX_LABEL_ID);
        if (!maxLabel) {
          return;
        }

        maxLabel.innerText = newValue;
        break;
      case 'min-range':
      case 'min':
        if (isNaN(newValue) || oldValue === newValue) {
          return;
        }

        this.minRange = newValue;
        break;
      case 'max-range':
      case 'max':
        if (isNaN(newValue) || oldValue === newValue) {
          return;
        }

        this.maxRange = newValue;
        break;
    }

    this.init();
  }

  connectedCallback() {
    this.init();
  }

  disconnectedCallback() {
    // Removing event listeners
    const slider = this.getEl(constants.SLIDER_ID);

    const min = slider.querySelector(`#${constants.MIN}`);
    this.removeEventListeners(
      min,
      constants.RANGE_STOPPED_EVENTS,
      this.emitRangeSelection,
      false
    );
    this.removeEventListeners(min, ['input'], this.onRangeInput, false);

    const max = slider.querySelector(`#${constants.MAX}`);
    this.removeEventListeners(
      max,
      constants.RANGE_STOPPED_EVENTS,
      this.emitRangeSelection,
      false
    );
    this.removeEventListeners(max, ['input'], this.onRangeInput, false);
  }

  dispatchCustomEvent(el, event) {
    const objToDispatchFrom = el ? el : window;
    objToDispatchFrom.dispatchEvent(event);
  }

  // Helper method to add event listeners for multiple events
  addMultipleEventListeners(element, events, handler) {
    events.forEach((e) => element.addEventListener(e, handler));
  }

  // Helper method to remove listeners for multiple events
  removeEventListeners(element, events, callBack, useCapture) {
    events.forEach((event) => {
      element.removeEventListener(event, callBack, useCapture);
    });
  }

  getEl(id) {
    return this.shadowRoot.getElementById(id);
  }

  // Setting the initial state of the application
  init() {
    const slider = this.getEl(constants.SLIDER_ID);

    this.setInitialSliderState(slider);
    this.setupColors();

    const min = slider.querySelector(`#${constants.MIN}`);
    const max = slider.querySelector(`#${constants.MAX}`);

    /* set data-values */
    min.setAttribute('data-value', this.minRange);
    max.setAttribute('data-value', this.maxRange);

    slider.setAttribute('data-range-width', slider.offsetWidth);

    this.createLabels(slider, min);
    this.createLegend(slider);

    const averageOfMinAndMax = (this.minRange + this.maxRange) / 2;
    this.draw(slider, averageOfMinAndMax);

    // Adding update event that updates the range selector
    min.addEventListener('input', this.onRangeInput);
    max.addEventListener('input', this.onRangeInput);

    // Adding events when the user stops selecting a range
    // this is then used to emit the events to whoever is
    // consuming this component. If you did it in the `update`
    // function it would be called hundreds of times, this allows
    // us to only call it when the input has stopped.
    this.addMultipleEventListeners(
      min,
      constants.RANGE_STOPPED_EVENTS,
      this.emitRangeSelection
    );
    this.addMultipleEventListeners(
      max,
      constants.RANGE_STOPPED_EVENTS,
      this.emitRangeSelection
    );
  }

  // Sets the initial inner HTML of the slider. This is necessary because the init()
  // function appends other elements downstream and if we don't reset it then things
  // will end up getting duplicated
  setInitialSliderState(slider) {
    slider.innerHTML = `
        <label id="${constants.MIN_LABEL_ID}" for="${constants.MIN}">Minimum</label> 
        <input id="${constants.MIN}" class="range-input" name="${constants.MIN}" type="range" step="1" />
        <label id="${constants.MAX_LABEL_ID}" for="${constants.MAX}">Maximum</label>
        <input id="${constants.MAX}" class="range-input" name="${constants.MAX}" type="range" step="1" />
      `;
  }

  // Emits new custom event for min-range-changed or max-range-changed so
  // that the consumer of this component can do whatever they need when
  // the values are changed
  emitRange() {
    const slider = this.getEl(constants.SLIDER_ID);
    const min = slider.querySelector(`#${constants.MIN}`);
    const max = slider.querySelector(`#${constants.MAX}`);

    this.dispatchCustomEvent(
      slider,
      new CustomEvent(this.eventNameToEmitOnChange, {
        bubbles: true,
        composed: true,
        detail: {
          sliderId: this.sliderId,
          minRangeValue: Math.floor(min.value),
          maxRangeValue: Math.floor(max.value),
        },
      })
    );
  }

  draw(slider, splitValue) {
    const min = slider.querySelector(`#${constants.MIN}`);
    min.setAttribute(constants.MIN, this.minRange);
    min.setAttribute(constants.MAX, splitValue);

    const max = slider.querySelector(`#${constants.MAX}`);
    max.setAttribute(constants.MIN, splitValue);
    max.setAttribute(constants.MAX, this.maxRange);

    const rangeWidth = parseInt(slider.getAttribute('data-range-width'));
    const thumbSize = cssHelpers.sliderCircleSize;

    min.style.width = `${parseInt(
      thumbSize +
        ((splitValue - this.minRange) / (this.maxRange - this.minRange)) *
          (rangeWidth - 2 * thumbSize)
    )}px`;
    max.style.width = `${parseInt(
      thumbSize +
        ((this.maxRange - splitValue) / (this.maxRange - this.minRange)) *
          (rangeWidth - 2 * thumbSize)
    )}px`;
    min.style.left = '0px';
    max.style.left = `${parseInt(min.style.width)}px`;

    const lower = slider.querySelector('.lower');

    let sliderHeight = min.offsetHeight;
    if (!this.hideLabel) {
      min.style.top = `${lower.offsetHeight}px`;
      max.style.top = `${lower.offsetHeight}px`;

      sliderHeight += lower.offsetHeight;
    }

    if (!this.hideLegend) {
      const legend = slider.querySelector('.legend');
      legend.style.paddingTop = `${min.offsetHeight}px`;

      sliderHeight += +legend.offsetHeight;
    }

    slider.style.height = `${sliderHeight}px`;

    if (max.value > this.maxRange - 1) {
      // Correcting if it's 1 off at the end
      max.setAttribute('data-value', this.maxRange);
    }

    max.value = max.getAttribute('data-value');
    min.value = min.getAttribute('data-value');

    if (!this.hideLabel) {
      const upper = slider.querySelector('.upper');

      if (this.inputsForLabels) {
        lower.value = min.getAttribute('data-value');
        upper.value = max.getAttribute('data-value');
      } else {
        lower.innerHTML = min.getAttribute('data-value');
        upper.innerHTML = max.getAttribute('data-value');
      }
    }
  }

  update(el) {
    const slider = el.parentElement;
    const min = slider.querySelector(`#${constants.MIN}`);
    const max = slider.querySelector(`#${constants.MAX}`);
    const minValue = Math.floor(min.value);
    const maxValue = Math.floor(max.value);

    // Setting the inactive values before draw
    min.setAttribute('data-value', minValue);
    max.setAttribute('data-value', maxValue);

    const averageOfMinAndMax = (minValue + maxValue) / 2;
    this.draw(slider, averageOfMinAndMax);
  }

  setupColors() {
    const elements = this.shadowRoot.querySelectorAll(
      '.min-max-slider > .range-input'
    );
    elements.forEach((el) => {
      if (this.sliderColor) {
        el.style.backgroundImage = `linear-gradient(to bottom, transparent 0%, transparent 30%, ${this.sliderColor} 30%, ${this.sliderColor} 60%, transparent 60%, transparent 100%)`;
      }

      if (this.circleColor) {
        el.style.setProperty('--sliderColor', this.circleColor);
      }

      if (this.circleBorderColor) {
        el.style.setProperty('--sliderBorderColor', this.circleBorderColor);
      }

      if (this.circleFocusBorderColor) {
        el.style.setProperty(
          '--sliderFocusBorderColor',
          this.circleFocusBorderColor
        );
      }
    });
  }

  createLegend(slider) {
    if (this.hideLegend) {
      return;
    }

    // Sets the legend values (the numbers below the slider bar
    // this is dynamic and can handle any number of items in the
    // legend, that's why there is a loop in the event you have
    // more than 2 values in the legend
    let legend = document.createElement('div');
    legend.classList.add('legend');
    let legendvalues = [];

    for (let i = 0; i < this.numberOfLegendItemsToShow; i++) {
      legendvalues[i] = document.createElement('div');
      const val = Math.round(
        this.minRange +
          (i / (this.numberOfLegendItemsToShow - 1)) *
            (this.maxRange - this.minRange)
      );
      legendvalues[i].appendChild(document.createTextNode(val));
      legend.appendChild(legendvalues[i]);
    }

    slider.appendChild(legend);
  }

  createLabels(slider, min) {
    if (this.hideLabel) {
      return;
    }

    const labelType = this.inputsForLabels ? 'input' : 'span';
    let lower = document.createElement(labelType);
    let upper = document.createElement(labelType);

    lower.classList.add(`range-${labelType}-label`, 'lower', 'value');
    upper.classList.add(`range-${labelType}-label`, 'upper', 'value');

    if (this.inputsForLabels) {
      lower.value = this.minRange;
      upper.value = this.maxRange;

      lower.setAttribute('type', 'number');
      lower.setAttribute('min', this.minRange);
      lower.setAttribute('max', this.maxRange);

      upper.setAttribute('type', 'number');
      upper.setAttribute('min', this.minRange);
      upper.setAttribute('max', this.maxRange);

      lower.addEventListener('input', this.onRangeInput);
      upper.addEventListener('input', this.onRangeInput);
    } else {
      lower.appendChild(document.createTextNode(this.minRange));
      upper.appendChild(document.createTextNode(this.maxRange));
    }

    slider.insertBefore(lower, min.previousElementSibling);
    slider.insertBefore(upper, min.previousElementSibling);

    if (this.inputsForLabels) {
      // Adding a "-" symbol beyween the range inputs since you cannot do
      // this via CSS pseudo (before/after) selectors on an input element
      let dashIcon = document.createElement('i');
      dashIcon.classList.add('range-input-dash-icon');
      dashIcon.setAttribute('aria-hidden', true);
      dashIcon.innerHTML = '&#65123';
      slider.insertBefore(
        dashIcon,
        min.previousElementSibling.previousElementSibling
      );
    }
  }
}

window.customElements.define('range-selector', SimpleRange);