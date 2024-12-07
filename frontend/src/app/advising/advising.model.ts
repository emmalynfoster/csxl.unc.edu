/**
 * @author Ife Babarinde, Emmalyn Foster
 * @copyright 2024
 * @license MIT
 */

export interface DropIn {
  id: number | null;
  title: string;
  start: Date;
  end: Date;
  link: string;
}

export interface DropInJson {
  id: number | null;
  title: string;
  start: string;
  end: string;
  link: string;
}

export const parseDropInJson = (responseModel: DropInJson): DropIn => {
  return {
    id: responseModel.id,
    title: responseModel.title,
    start: new Date(responseModel.start), // Convert string to Date
    end: new Date(responseModel.end), // Convert string to Date
    link: responseModel.link
  };
};

export interface DocumentSection {
  id: number | null;
  title: string;
  content: string;
  document_id: number;
}

export interface DocumentDetails {
  id: number | null;
  title: string;
  link: string;
}
