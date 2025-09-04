# Frontend Architecture Documentation

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── ui/              # Reusable UI components
│   │   ├── Button.js
│   │   ├── Card.js
│   │   ├── Input.js
│   │   ├── Textarea.js
│   │   ├── Modal.js
│   │   ├── LoadingSpinner.js
│   │   ├── StatusMessage.js
│   │   └── index.js
│   ├── StudyInterface.js # Main study component
│   ├── CreateCard.js     # Card creation component
│   ├── ManageCards.js    # Card management component
│   └── FlipCard.js       # Flip animation component
├── hooks/               # Custom React hooks
│   ├── useFlashcards.js # Flashcard data management
│   ├── useStudy.js      # Study session management
│   ├── useForm.js       # Form state management
│   └── index.js
├── services/            # API and external services
│   └── api.js          # API service layer
├── utils/               # Utility functions
│   └── index.js        # Helper functions
├── constants/           # Application constants
│   └── index.js        # Configuration and constants
├── styles/              # CSS modules and styles
│   └── components.css  # UI component styles
├── App.js              # Main application component
├── index.js            # Application entry point
└── index.css           # Global styles
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **Components**: Focus only on UI rendering and user interactions
- **Hooks**: Handle state management and business logic
- **Services**: Manage external API calls and data fetching
- **Utils**: Provide pure functions for data transformation

### 2. **Single Responsibility Principle**
- Each component has a single, well-defined purpose
- Hooks are focused on specific functionality (forms, API calls, study logic)
- Utility functions are pure and reusable

### 3. **Dependency Inversion**
- Components depend on abstractions (hooks) rather than concrete implementations
- API calls are abstracted through service layer
- Configuration is externalized to constants

### 4. **Reusability**
- UI components are generic and reusable across the application
- Hooks can be used by multiple components
- Utility functions are pure and context-independent

## 🧩 Component Architecture

### UI Components (`components/ui/`)
Reusable, presentation-only components with consistent API:

```javascript
// Example: Button component
<Button 
  variant="primary" 
  size="large" 
  loading={isLoading}
  onClick={handleClick}
>
  Submit
</Button>
```

**Features:**
- PropTypes validation for type safety
- Consistent styling and behavior
- Accessibility support
- Loading and disabled states

### Feature Components (`components/`)
Business logic components that compose UI components:

```javascript
// Example: StudyInterface component
const StudyInterface = () => {
  const { currentCard, loading, submitReview } = useStudy();
  
  return (
    <FlipCard 
      card={currentCard}
      onReview={submitReview}
      loading={loading}
    />
  );
};
```

## 🎣 Custom Hooks

### `useFlashcards()`
Manages flashcard CRUD operations:

```javascript
const {
  cards,           // Array of flashcards
  loading,         // Loading state
  error,           // Error message
  createCard,      // Function to create card
  updateCard,      // Function to update card
  deleteCard,      // Function to delete card
  refreshCards,    // Function to refresh data
} = useFlashcards();
```

### `useStudy()`
Handles study session logic:

```javascript
const {
  currentCard,        // Current card for review
  showDefinition,     // Whether definition is visible
  loading,            // Loading state
  submitReview,       // Function to submit review
  loadNextCard,       // Function to load next card
} = useStudy();
```

### `useForm()`
Generic form state management:

```javascript
const {
  values,          // Form values object
  errors,          // Validation errors
  isSubmitting,    // Submission state
  handleChange,    // Input change handler
  handleSubmit,    // Form submission handler
  resetForm,       // Reset form function
} = useForm(initialValues, onSubmit);
```

## 🔧 Services Layer

### API Service (`services/api.js`)
Centralized API communication with:

- **Request/Response Interceptors**: Logging and error handling
- **Error Transformation**: Consistent error messages
- **Service Separation**: Flashcard and Study services
- **Type Safety**: Structured request/response handling

```javascript
// Usage example
import { flashcardService, studyService } from '../services/api';

const card = await flashcardService.createFlashcard(word, definition);
const nextCard = await studyService.getNextCard();
```

## 🛠 Utilities

### Helper Functions (`utils/index.js`)
Pure functions for common operations:

```javascript
import { formatBinNumber, getCardStatusColor, truncateText } from '../utils';

const binName = formatBinNumber(3); // "2m"
const color = getCardStatusColor(card); // "#27ae60"
const preview = truncateText(text, 100); // "Long text..."
```

## 📋 Constants

### Configuration (`constants/index.js`)
Centralized configuration and constants:

```javascript
import { SPACED_REPETITION, MESSAGES, API_CONFIG } from '../constants';

const binName = SPACED_REPETITION.BIN_NAMES[1]; // "5s"
const errorMsg = MESSAGES.ERROR_NETWORK; // "Network error..."
const apiUrl = API_CONFIG.BASE_URL; // "http://localhost:8000"
```

## 🎨 Styling Strategy

### Component-Scoped Styles
- **UI Components**: Self-contained styles in `styles/components.css`
- **Responsive Design**: Mobile-first approach
- **CSS Variables**: For consistent theming
- **BEM Methodology**: Clear class naming conventions

### Style Organization
```css
/* UI Component Styles */
.button { /* Base button styles */ }
.button-primary { /* Primary variant */ }
.button-small { /* Size variant */ }
.button-disabled { /* State modifier */ }
```

## 🚀 Best Practices Implemented

### 1. **Error Handling**
- Centralized error handling in API service
- User-friendly error messages
- Graceful fallbacks for failed operations

### 2. **Performance**
- React.memo for expensive components
- Lazy loading for routes
- Debounced user inputs
- Optimized re-renders with useCallback

### 3. **Accessibility**
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

### 4. **Type Safety**
- PropTypes validation for all components
- Consistent API interfaces
- Runtime type checking

### 5. **Testing Ready**
- Pure functions for easy unit testing
- Separated business logic from UI
- Mock-friendly service layer
- Isolated component concerns

## 📈 Scalability Features

### 1. **Easy Extension**
- Add new UI components to `ui/` folder
- Create new hooks for specific functionality
- Extend API service with new endpoints
- Add new constants and utilities as needed

### 2. **Code Splitting**
- Components can be easily code-split
- Services can be lazy-loaded
- Hooks can be conditionally imported

### 3. **State Management Ready**
- Architecture supports Redux/Zustand integration
- Hooks can be easily converted to global state
- Service layer supports caching strategies

## 🔄 Migration Benefits

### Before (Monolithic Components)
- Mixed concerns in single files
- Repeated logic across components
- Hard to test and maintain
- Tight coupling between UI and business logic

### After (Modular Architecture)
- Clear separation of concerns
- Reusable components and logic
- Easy to test and maintain
- Loose coupling with dependency injection

This modular architecture provides a solid foundation for scaling the application while maintaining code quality and developer experience.
